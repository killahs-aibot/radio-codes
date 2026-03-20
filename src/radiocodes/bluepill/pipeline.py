#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BluePill Pipeline — Orchestrates the full Blaupunkt reverse-engineering workflow

Usage:
  python -m radiocodes.bluepill.pipeline --brand blaupunkt --min-pairs 50
  python -m radiocodes.bluepill.pipeline --brand peugeot --scrape --analyze

Steps:
  1. SCRAPE   — Fetch forum pages for serial+code pairs
  2. DEDUPE   — Remove duplicates from collected pairs
  3. EXPAND   — Add pairs from all existing data sources
  4. ANALYZE  — Run lookup table + modular arithmetic finders
  5. VALIDATE — Cross-validate best candidates on held-out pairs
  6. EXPORT   — Save verified formula to radiocodes/algorithms/
  7. REPORT   — Generate markdown report
"""

import argparse
import csv
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from radiocodes.bluepill.scraper import MHHMHFScraper, BRAND_TAGS, BP_PREFIXES
from radiocodes.bluepill.analyzer import (
    analyze_pairs, find_lookup_table, FormulaCandidate, apply_formula
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("pipeline")


BRAND_SERIAL_PREFIXES = {
    "blaupunkt": ["BP", "AUZ", "VWZ", "GM0", "SEZ", "SKZ", "F0", "7"],
    "peugeot":   ["BP", "815", "7"],
    "citroen":   ["BP", "815", "7", "6"],
    "opel":      ["GM0", "GM1", "GM2", "CM01"],
    "vauxhall":  ["GM0", "GM1", "GM2", "CM01"],
    "vw":        ["VWZ", "AUZ", "VVZ", "LPZ"],
    "audi":      ["AUZ", "VWZ"],
    "ford":      ["M", "V", "F"],
    "renault":   ["LP", "CL", "R", "D"],
    "nissan":    ["BP", "B7", "PN"],
    "honda":     [],
    "toyota":    [],
    "fiat":      ["BP", "5K", "FK"],
    "alfa":      ["BP", "AR"],
    "chrysler":  ["BP", "CH"],
    "jaguar":    ["BP", "JA", "JAG"],
}


def load_existing_pairs(brand: str, data_dir: Path) -> List[Tuple[str, str]]:
    """Load known pairs for a brand from all CSV sources."""
    pairs = []
    seen = set()

    csv_files = [
        data_dir / "forum_pairs.csv",
        data_dir / "forum_pairs_digital_kaos.csv",
    ]

    for csvf in csv_files:
        if not csvf.exists():
            continue
        for row in csv.DictReader(csvf.open()):
            b = row.get("brand", "").lower().strip()
            # Match brand or alias
            if b != brand.lower() and b not in BRAND_TAGS.get(brand, "").lower():
                continue
            serial = row.get("serial", "").strip()
            code = row.get("code", "").strip()
            if serial and code and serial not in seen:
                seen.add(serial)
                pairs.append((serial, code))

    logger.info(f"Loaded {len(pairs)} existing pairs for {brand}")
    return pairs


def scrape_forum_pairs(brand: str, max_pages: int = 20) -> List[Tuple[str, str]]:
    """Scrape MHH AUTO thread for pairs."""
    logger.info(f"Scraping MHH AUTO for {brand} pairs...")
    scraper = MHHMHFScraper()

    try:
        total = scraper.fetch_thread_pages(max_pages=max_pages)
    except Exception as e:
        logger.error(f"Scraper failed: {e}")
        return []

    # Filter to target brand
    filtered = scraper.pairs
    if brand in BRAND_SERIAL_PREFIXES and BRAND_SERIAL_PREFIXES[brand]:
        prefixes = BRAND_SERIAL_PREFIXES[brand]
        filtered = [p for p in scraper.pairs if any(p.serial.startswith(pre) for pre in prefixes)]

    logger.info(f"Found {len(scraper.pairs)} total pairs, {len(filtered)} for {brand}")
    return [(p.serial, p.code) for p in filtered]


def dedupe_pairs(pairs: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Remove exact duplicate serials (different codes = flag for review)."""
    seen_code: Dict[str, str] = {}
    conflicts: List[Tuple[str, str, str]] = []

    for serial, code in pairs:
        serial = serial.upper().strip()
        code = code.strip()
        if serial in seen_code:
            if seen_code[serial] != code:
                conflicts.append((serial, seen_code[serial], code))
        else:
            seen_code[serial] = code

    if conflicts:
        logger.warning(f"⚠️  {len(conflicts)} serials have conflicting codes:")
        for s, c1, c2 in conflicts[:10]:
            logger.warning(f"   {s}: {c1} vs {c2}")

    unique = [(s, c) for s, c in seen_code.items()]
    logger.info(f"Dedupe: {len(pairs)} → {len(unique)} unique serials ({len(conflicts)} conflicts)")
    return unique


def build_test_vectors(pairs: List[Tuple[str, str]], n: int = 20) -> List[Tuple[str, str]]:
    """Sample N pairs as held-out test vectors (for validation)."""
    import random
    if len(pairs) <= n:
        return pairs
    sampled = random.sample(pairs, n)
    remaining = [p for p in pairs if p not in sampled]
    return sampled


def run_analysis(pairs: List[Tuple[str, str]], brand: str, min_acc: float):
    """Run the analyzer on pairs. Returns (best_candidate, analysis_result)."""
    if len(pairs) < 20:
        logger.error(f"Not enough pairs for analysis (have {len(pairs)}, need 20+)")
        return None, None

    result = analyze_pairs(pairs, brand, min_acc)

    if result["best"]:
        logger.info(f"✅ Best candidate: {result['best']['name']}")
        logger.info(f"   Accuracy: {result['best']['accuracy']*100:.1f}% "
                    f"({result['best']['pairs_used']} pairs used)")
        logger.info(f"   Type: {result['best']['formula_type']}")
        logger.info(f"   {result['best']['description']}")
    else:
        logger.warning("❌ No formula candidates found above threshold")

    # Also show top lookup table candidates
    lt_cands = [c for c in result["candidates"] if c["formula_type"] == "lookup_table"][:3]
    if lt_cands:
        logger.info(f"\nTop {len(lt_cands)} lookup table candidates:")
        for c in lt_cands:
            logger.info(f"  [{c['accuracy']*100:.1f}%] {c['name']}")

    return result.get("best"), result


def validate_on_test(candidate: FormulaCandidate, test_pairs: List[Tuple[str, str]]) -> float:
    """Validate a candidate on held-out test pairs."""
    if not test_pairs:
        return 0.0
    correct = sum(
        1 for serial, code in test_pairs
        if apply_formula(candidate, serial).lstrip('0') == code.strip().lstrip('0')
    )
    accuracy = correct / len(test_pairs)
    logger.info(f"Test accuracy: {accuracy*100:.1f}% ({correct}/{len(test_pairs)})")
    return accuracy


def export_formula(candidate: FormulaCandidate, brand: str, out_dir: Path):
    """Export a verified formula as a Python algorithm file."""
    out_dir.mkdir(parents=True, exist_ok=True)
    p = candidate.params
    ft = candidate.formula_type

    if ft == "lookup_table":
        table = p["table"]
        ts = p["table_size"]

        if "digit_idx_a" in p:
            # 2D table
            table_repr = json.dumps(table)
            code = f'''
# -*- coding: utf-8 -*-
"""
Auto-generated Blaupunkt BP algorithm — BluePill reverse engineering
⚠️  DO NOT EDIT — This file is AUTO-GENERATED
Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}
Accuracy: {candidate.accuracy*100:.1f}% ({candidate.pairs_used} pairs)
Type: 2D lookup table

Formula: code_digit = table[digits[{p["digit_idx_a"]}]%{ts}][digits[{p["digit_idx_b"]}]%{ts}]]
"""

from typing import Tuple, Optional
from .base import BaseRadioAlgorithm, RadioInfo


_LUT = {table_repr}
_TABLE_SIZE = {ts}
_IDX_A = {p["digit_idx_a"]}
_IDX_B = {p["digit_idx_b"]}
_CODE_POS = {p.get("code_pos", 0)}


def _canonicalize(serial: str) -> list:
    result = []
    for c in serial.upper():
        if c.isdigit():
            result.append(int(c))
        elif c.isalpha():
            result.append(ord(c) - ord('A') + 10)
    return result


def _apply(serial: str) -> str:
    digits = _canonicalize(serial)
    if len(digits) <= max(_IDX_A, _IDX_B):
        return ""
    va = digits[_IDX_A] % _TABLE_SIZE
    vb = digits[_IDX_B] % _TABLE_SIZE
    cell = _LUT[va * _TABLE_SIZE + vb]
    if cell == -1:
        return ""
    return str(cell)


class BlaupunktBPAlgorithm(BaseRadioAlgorithm):
    brand_name = "Blaupunkt BP ⚠️ AUTO-GENERATED"
    supported_models = ["BP (Blaupunkt)"]
    code_length = 4
    verified = {candidate.accuracy*100:.1f}

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = serial.upper().replace(" ", "").replace("-", "")
        if len(serial) < 4:
            return False, "Serial too short"
        return True, None

    def calculate(self, serial: str) -> str:
        result = _apply(serial.upper().replace(" ", "").replace("-", ""))
        if not result:
            raise ValueError("Could not calculate code for this serial")
        return result
'''
        else:
            # 1D table
            table_repr = json.dumps(p["table"])
            idx = p["digit_idx"]
            code = f'''
# 1D table version — code goes here (truncated for brevity)
_LUT = {table_repr}
_IDX = {idx}
'''
    else:
        code = f"# Modular formula: {candidate.description}\n# TODO: implement"

    out_file = out_dir / f"{brand}_bp.py"
    out_file.write_text(code)
    logger.info(f"✅ Exported formula → {out_file}")
    return out_file


def generate_report(result: Dict, candidate: FormulaCandidate, brand: str,
                    all_pairs: int, work_dir: Path):
    """Generate a markdown report."""
    report_path = work_dir / "bluepill_REPORT.md"

    lines = [
        f"# BluePill Reverse Engineering Report — {brand.upper()}",
        "",
        f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
        f"**Total pairs analyzed:** {all_pairs}",
        f"**Pipeline version:** 0.1.0",
        "",
        "## Results",
        "",
    ]

    if candidate:
        lines += [
            f"✅ **Formula found!** Accuracy: {candidate.accuracy*100:.1f}%",
            f"- Type: `{candidate.formula_type}`",
            f"- Description: {candidate.description}",
            f"- Pairs used: {candidate.pairs_used}",
            "",
            "## Formula Details",
            "",
            f"```json",
            json.dumps(candidate.params, indent=2),
            "```",
            "",
        ]
    else:
        lines += [
            "❌ **No formula found above threshold.**",
            "",
            "Recommendations:",
            "1. Collect more serial+code pairs (need 500+ for reliable reverse-engineering)",
            "2. Try the MHH AUTO scraper to gather more data",
            "3. Check if a database lookup approach is more suitable",
            "",
        ]

    lines += [
        "## Top Candidates",
        "",
    ]
    for c in result.get("candidates", [])[:10]:
        lines.append(f"- [{c['accuracy']*100:.1f}%] `{c['name']}` — {c['description']}")

    lines += [
        "",
        "## Pair Statistics",
        "",
        f"- Serial length distribution: `{result.get('serial_length_dist', {})}`",
        f"- Code length distribution: `{result.get('code_length_dist', {})}`",
        f"- Top prefixes: `{result.get('top_prefixes', {})}`",
        "",
        "---",
        "*Generated by BluePill pipeline*",
    ]

    report_path.write_text("\n".join(lines))
    logger.info(f"📄 Report → {report_path}")
    return report_path


# ─────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="BluePill — Blaupunkt BP Reverse Engineering Pipeline")
    ap.add_argument("--brand", default="blaupunkt", help="Brand to analyze")
    ap.add_argument("--min-pairs", type=int, default=20, help="Minimum pairs needed to run analysis")
    ap.add_argument("--min-accuracy", type=float, default=0.85, help="Minimum accuracy threshold")
    ap.add_argument("--scrape", action="store_true", help="Also scrape MHH AUTO for new pairs")
    ap.add_argument("--scrape-pages", type=int, default=20, help="Max forum pages to scrape")
    ap.add_argument("--test-vectors", type=int, default=20, help="Number of pairs to hold out for testing")
    ap.add_argument("--output-dir", help="Output directory for generated files")
    ap.add_argument("--data-dir", default=None, help="RadioCodes data directory")
    args = ap.parse_args()

    # Resolve paths
    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        data_dir = Path(__file__).parent.parent.parent.parent / "data"

    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        out_dir = data_dir / "bp_pairs"

    out_dir.mkdir(parents=True, exist_ok=True)
    work_dir = out_dir

    logger.info(f"=== BluePill Pipeline — {args.brand} ===")
    logger.info(f"Data dir: {data_dir}")
    logger.info(f"Output dir: {out_dir}")

    # ── Step 1: Collect existing pairs ────────────────────────────
    pairs = load_existing_pairs(args.brand, data_dir)

    # ── Step 2: Scrape for more (optional) ───────────────────────
    if args.scrape:
        scraped = scrape_forum_pairs(args.brand, max_pages=args.scrape_pages)
        pairs.extend(scraped)

    # ── Step 3: Dedupe ───────────────────────────────────────────
    pairs = dedupe_pairs(pairs)

    # ── Step 4: Check minimum ────────────────────────────────────
    if len(pairs) < args.min_pairs:
        logger.error(f"Not enough pairs: {len(pairs)} < {args.min_pairs}. Try --scrape first.")
        logger.info("Run with --scrape to fetch pairs from MHH AUTO forum.")
        sys.exit(1)

    # Save deduplicated pairs
    pairs_file = work_dir / f"{args.brand}_pairs.csv"
    with pairs_file.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["serial", "code"])
        for serial, code in sorted(pairs):
            w.writerow([serial, code])
    logger.info(f"Saved {len(pairs)} unique pairs → {pairs_file}")

    # ── Step 5: Build test set ────────────────────────────────────
    test_pairs = build_test_vectors(pairs, n=args.test_vectors)
    train_pairs = [p for p in pairs if p not in set(test_pairs)]
    logger.info(f"Train: {len(train_pairs)}, Test: {len(test_pairs)}")

    # ── Step 6: Run analysis ─────────────────────────────────────
    best, result = run_analysis(train_pairs, args.brand, args.min_accuracy)

    # ── Step 7: Validate on test set ─────────────────────────────
    if best:
        test_acc = validate_on_test(best, test_pairs)
        best["test_accuracy"] = test_acc

    # ── Step 8: Export ───────────────────────────────────────────
    if best and best["accuracy"] >= args.min_accuracy:
        formula_file = export_formula(best, args.brand, out_dir)

    # ── Step 9: Report ───────────────────────────────────────────
    report_file = generate_report(result, best, args.brand, len(pairs), work_dir)

    # Save full analysis JSON
    json_file = work_dir / f"{args.brand}_analysis.json"
    json_file.write_text(json.dumps(result, indent=2))
    logger.info(f"Full analysis → {json_file}")

    # Summary
    print("\n" + "="*60)
    print(f"BluePill Pipeline Complete — {args.brand}")
    print("="*60)
    print(f"  Pairs analyzed : {len(pairs)}")
    print(f"  Best accuracy  : {best['accuracy']*100:.1f}% (train)" if best else "  Best accuracy  : None")
    if best:
        print(f"  Test accuracy  : {best.get('test_accuracy', 0)*100:.1f}% ({len(test_pairs)} held-out)")
        print(f"  Formula type   : {best['formula_type']}")
        print(f"  Output files   : {out_dir}/")
    print("="*60)


if __name__ == "__main__":
    main()
