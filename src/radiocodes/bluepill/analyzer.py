# -*- coding: utf-8 -*-
"""
BluePill Analyzer — Reverse-engineer lookup tables from serial+code pairs

Given enough (serial, code) pairs for a radio brand, this module tries to
reverse the algorithm by finding lookup tables and algebraic transforms.

The approach:
1. Canonicalize serials → numeric form (digits + letter-values)
2. Try to find fixed-position lookup tables (Ford M style: digit[i] → row/col)
3. Try modular arithmetic transforms
4. Cross-validate found formulas against held-out pairs

The Ford M Series algorithm is the gold standard we're looking for:
- 10×10 lookup table indexed by specific serial digits
- Chained modulo operations
- If we find 500+ pairs for Blaupunkt BP, similar structure is possible
"""

import json
import logging
import math
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Set
from itertools import product, combinations
from pathlib import Path

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────────

@dataclass
class FormulaCandidate:
    """A candidate formula that maps serial → code."""
    name: str
    description: str
    # JSON-serializable params (lookup tables, coefficients, etc.)
    params: dict
    accuracy: float       # % of pairs correctly predicted
    pairs_used: int
    test_pairs: int
    formula_type: str     # "lookup_table", "modular", "linear", "polynomial"
    source_file: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# ─────────────────────────────────────────────────────────────────
# Serial canonicalizers
# Convert different serial formats → numeric digit sequences
# ─────────────────────────────────────────────────────────────────

def canonicalize_digits(serial: str) -> List[int]:
    """
    Convert serial to list of digits.
    Letters → their alphabet position (A=10, B=11, ... Z=35)
    All other chars → dropped.
    """
    result = []
    for c in serial.upper():
        if c.isdigit():
            result.append(int(c))
        elif c.isalpha():
            val = ord(c) - ord('A') + 10
            result.append(val)
    return result


def canonicalize_digits_bounded(serial: str, max_val: int = 9) -> List[int]:
    """
    Like canonicalize_digits but clamps values to max_val.
    Used when we know the algorithm operates on 0-9 only.
    """
    result = []
    for c in serial.upper():
        if c.isdigit():
            result.append(int(c))
        elif c.isalpha():
            val = ord(c) - ord('A') + 10
            result.append(min(val, max_val))
    return result


def canonicalize_raw_digits(serial: str) -> List[int]:
    """Extract raw digits only (ignore letters)."""
    return [int(c) for c in serial if c.isdigit()]


# ─────────────────────────────────────────────────────────────────
# Lookup table finder
# Tries to find Ford M style: digit[i] → row/col → table value
# ─────────────────────────────────────────────────────────────────

def find_lookup_table(pairs: List[Tuple[str, str]], min_accuracy: float = 0.90) -> List[FormulaCandidate]:
    """
    Try to find a 10×10 (or other size) lookup table that maps
    specific serial digit positions to code digits.

    Ford M style algorithm structure:
      code[i] = table_row_col[digit_pos[n]] where row/col come from
      specific serial positions, then chained modulo-10 ops.

    This searches for:
    1. Single-digit → single-digit direct mapping (1-digit table)
    2. Two-digits → one code digit (10×10 table indexed by two serial digits)
    3. Three-digits → one code digit (10×10×10 cube, but we only search 10×10)

    Returns list of candidates sorted by accuracy.
    """
    candidates = []

    # Convert pairs to numeric form
    # We try raw digits and canonicalized digits
    num_pairs = []
    for serial, code in pairs:
        digits = canonicalize_digits(serial)
        code_digits = [int(c) for c in code.strip().lstrip('0').zfill(len(code))]
        if len(digits) >= 4 and len(code_digits) >= 3:
            num_pairs.append((digits, code_digits))

    if len(num_pairs) < 20:
        logger.warning(f"Not enough pairs to analyze (have {len(num_pairs)}, need 20+)")
        return candidates

    # ── Strategy 1: Two-digit indexed lookup tables ──────────────────
    # code_digit[i] ≈ lookup_table[digits[a], digits[b]] % 10
    for code_pos in range(min(4, len(num_pairs[0][1]))):
        for idx_a in range(min(6, len(num_pairs[0][0]))):
            for idx_b in range(min(6, len(num_pairs[0][0]))):
                if idx_a == idx_b:
                    continue
                candidates.extend(
                    _find_2d_table(num_pairs, code_pos, idx_a, idx_b, min_accuracy)
                )

    # ── Strategy 2: Single-digit indexed tables ─────────────────────
    # code_digit[i] ≈ lookup_table[digits[idx]] % 10
    for code_pos in range(min(4, len(num_pairs[0][1]))):
        for idx in range(min(6, len(num_pairs[0][0]))):
            candidates.extend(
                _find_1d_table(num_pairs, code_pos, idx, min_accuracy)
            )

    # Sort by accuracy descending, then by pairs_used descending
    candidates.sort(key=lambda c: (-c.accuracy, -c.pairs_used))

    return candidates[:10]


def _find_1d_table(pairs, code_pos, idx, min_accuracy) -> List[FormulaCandidate]:
    """Find a 1D lookup table mapping digits[idx] → code_digit[code_pos]."""
    candidates = []

    for table_size in [10, 11, 12, 13, 14, 15, 16, 20, 26, 35]:
        table = [None] * table_size
        table_counts = [0] * table_size

        for digits, code_digits in pairs:
            if idx >= len(digits):
                continue
            val = digits[idx] % table_size
            if code_pos >= len(code_digits):
                continue
            target = code_digits[code_pos] % 10

            if table[val] is None:
                table[val] = target
            elif table[val] != target:
                table[val] = -1  # conflict

        if None in table or -1 in table:
            continue

        # Validate
        correct = 0
        total = 0
        for digits, code_digits in pairs:
            if idx < len(digits) and code_pos < len(code_digits):
                val = digits[idx] % table_size
                if table[val] == code_digits[code_pos] % 10:
                    correct += 1
                total += 1

        if total == 0:
            continue

        accuracy = correct / total
        if accuracy >= min_accuracy:
            # Round to 4 significant digits
            accuracy = round(accuracy, 4)
            candidates.append(FormulaCandidate(
                name=f"1D_table[digits[{idx}]]→code[{code_pos}]",
                description=f"10×{table_size} lookup table: code_digit[{code_pos}] = table[digits[{idx}] % {table_size}] % 10",
                params={"table": table, "table_size": table_size, "digit_idx": idx, "code_pos": code_pos},
                accuracy=accuracy,
                pairs_used=len(pairs),
                test_pairs=0,
                formula_type="lookup_table",
            ))

    return candidates


def _find_2d_table(pairs, code_pos, idx_a, idx_b, min_accuracy) -> List[FormulaCandidate]:
    """Find a 2D 10×10 lookup table mapping (digits[a], digits[b]) → code_digit."""
    candidates = []

    for table_size in [10, 11, 12]:
        table = [[None] * table_size for _ in range(table_size)]
        conflicts = defaultdict(int)

        for digits, code_digits in pairs:
            if idx_a >= len(digits) or idx_b >= len(digits):
                continue
            if code_pos >= len(code_digits):
                continue
            val_a = digits[idx_a] % table_size
            val_b = digits[idx_b] % table_size
            target = code_digits[code_pos] % 10

            if table[val_a][val_b] is None:
                table[val_a][val_b] = target
            elif table[val_a][val_b] != target:
                conflicts[(val_a, val_b)] += 1

        # Remove conflicts
        for (va, vb) in conflicts:
            table[va][vb] = None

        # Check for None cells (unfilled entries are OK if we have high coverage)
        filled = sum(1 for row in table for cell in row if cell is not None)
        total_cells = table_size * table_size
        coverage = filled / total_cells

        if coverage < 0.50:
            continue  # Need at least 50% of table filled

        # Validate
        correct = 0
        total = 0
        for digits, code_digits in pairs:
            if idx_a < len(digits) and idx_b < len(digits) and code_pos < len(code_digits):
                val_a = digits[idx_a] % table_size
                val_b = digits[idx_b] % table_size
                if table[val_a][val_b] is not None:
                    if table[val_a][val_b] == code_digits[code_pos] % 10:
                        correct += 1
                    total += 1

        if total < 10:
            continue

        accuracy = correct / total
        if accuracy >= min_accuracy:
            accuracy = round(accuracy, 4)
            # Flatten table for JSON serialization
            flat = [cell if cell is not None else -1 for row in table for cell in row]
            candidates.append(FormulaCandidate(
                name=f"2D_table[digits[{idx_a}],digits[{idx_b}]]→code[{code_pos}]",
                description=f"{table_size}×{table_size} lookup table: code_digit[{code_pos}] = table[digits[{idx_a}]%{table_size}][digits[{idx_b}]%{table_size}] % 10",
                params={
                    "table": flat,
                    "table_size": table_size,
                    "digit_idx_a": idx_a,
                    "digit_idx_b": idx_b,
                    "code_pos": code_pos,
                    "coverage": round(coverage, 3),
                },
                accuracy=accuracy,
                pairs_used=len(pairs),
                test_pairs=0,
                formula_type="lookup_table",
            ))

    return candidates


# ─────────────────────────────────────────────────────────────────
# Modular arithmetic finder
# Tries to find simple transforms: (a*X + b) % m = code
# ─────────────────────────────────────────────────────────────────

def find_modular(pairs: List[Tuple[str, str]], min_accuracy: float = 0.90) -> List[FormulaCandidate]:
    """
    Try to find modular arithmetic formulas of the form:
      code_digit[i] = (a * serial_digit[pos] + b) % m

    Also tries:
      code_digit[i] = (a * serial_digit[pos_a] + b * serial_digit[pos_b] + c) % m
      code = (prefix_num * a + b) % 10000
    """
    candidates = []

    # Canonicalize all pairs to (digits list, code_digits list)
    num_pairs = []
    for serial, code in pairs:
        digits = canonicalize_digits(serial)
        code_int = int(code.strip().lstrip('0') or '0')
        num_pairs.append((digits, code_int))

    if len(num_pairs) < 10:
        return candidates

    # ── Strategy 1: Linear modular for full code ───────────────────
    # code = (a * serial_prefix_num + b) % 10000 (or similar)
    for num_digits in [4, 5, 6, 7]:
        prefix_vals = []
        code_vals = []
        for digits, code in num_pairs:
            if len(digits) >= num_digits:
                # Use first N digits as a number
                prefix = sum(digits[i] * (10 ** (num_digits - 1 - i)) for i in range(min(num_digits, len(digits))))
                prefix %= 100000
                code_val = code % 10000
                prefix_vals.append(prefix)
                code_vals.append(code_val)

        if len(prefix_vals) < 10:
            continue

        # Try different moduli and coefficients
        for mod in [997, 1000, 1001, 1009, 1013, 2000, 2003, 5000, 9973, 10000]:
            for a in range(1, 100, 3):
                for b in range(0, 1000, 50):
                    correct = 0
                    for pv, cv in zip(prefix_vals, code_vals):
                        if (a * pv + b) % mod == cv % mod:
                            correct += 1
                    accuracy = correct / len(prefix_vals)
                    if accuracy >= min_accuracy:
                        candidates.append(FormulaCandidate(
                            name=f"linear_mod_{num_digits}d_a{a}_b{b}_mod{mod}",
                            description=f"code = ({a} * serial_prefix_{num_digits}d + {b}) % {mod}",
                            params={"a": a, "b": b, "mod": mod, "num_digits": num_digits},
                            accuracy=round(accuracy, 4),
                            pairs_used=len(num_pairs),
                            test_pairs=0,
                            formula_type="modular_linear",
                        ))

    # Sort and dedupe
    candidates.sort(key=lambda c: (-c.accuracy, -c.pairs_used))
    return candidates[:5]


# ─────────────────────────────────────────────────────────────────
# Cross-validation
# ─────────────────────────────────────────────────────────────────

def cross_validate(candidate: FormulaCandidate, pairs: List[Tuple[str, str]], holdout: float = 0.2) -> FormulaCandidate:
    """Test candidate on held-out pairs. Returns updated candidate with test accuracy."""
    import random
    random.shuffle(pairs)
    split = int(len(pairs) * (1 - holdout))
    train = pairs[:split]
    test = pairs[split:]

    if len(test) < 3:
        return candidate

    # Re-compute accuracy on test set
    correct = 0
    for serial, code in test:
        predicted = apply_formula(candidate, serial)
        if predicted == code.strip().lstrip('0').zfill(len(code)):
            correct += 1

    candidate.test_pairs = len(test)
    candidate.accuracy = round(correct / len(test), 4)
    return candidate


def apply_formula(candidate: FormulaCandidate, serial: str) -> str:
    """Apply a found formula to a serial. Returns predicted code string."""
    ft = candidate.formula_type
    p = candidate.params

    if ft == "lookup_table":
        digits = canonicalize_digits(serial)
        if "table_size" not in p:
            return ""
        ts = p["table_size"]

        if "digit_idx_a" in p and "digit_idx_b" in p:
            # 2D table
            idx_a = p["digit_idx_a"]
            idx_b = p["digit_idx_b"]
            code_pos = p["code_pos"]
            if idx_a >= len(digits) or idx_b >= len(digits):
                return ""
            flat = p["table"]
            val_a = digits[idx_a] % ts
            val_b = digits[idx_b] % ts
            cell = flat[val_a * ts + val_b]
            if cell == -1:
                return ""
            return str(cell)
        elif "digit_idx" in p:
            # 1D table
            idx = p["digit_idx"]
            code_pos = p["code_pos"]
            if idx >= len(digits):
                return ""
            table = p["table"]
            val = digits[idx] % ts
            return str(table[val])
    elif ft == "modular_linear":
        digits = canonicalize_digits(serial)
        nd = p["num_digits"]
        if len(digits) < nd:
            return ""
        prefix = sum(digits[i] * (10 ** (nd - 1 - i)) for i in range(min(nd, len(digits))))
        a, b, mod = p["a"], p["b"], p["mod"]
        result = (a * prefix + b) % mod
        return str(result).zfill(4)

    return ""


# ─────────────────────────────────────────────────────────────────
# Main analysis entry point
# ─────────────────────────────────────────────────────────────────

def analyze_pairs(pairs: List[Tuple[str, str]], brand: str = "unknown", min_accuracy: float = 0.90) -> Dict:
    """
    Run full analysis pipeline on a list of (serial, code) pairs.

    Returns a dict with:
      - candidates: list of FormulaCandidate dicts
      - best: the top candidate
      - stats: pair counts, digit lengths, etc.
    """
    logger.info(f"Analyzing {len(pairs)} pairs for brand={brand}")

    # Basic stats
    serial_lens = defaultdict(int)
    code_lens = defaultdict(int)
    prefixes = defaultdict(int)

    for serial, code in pairs:
        serial_lens[len(serial)] += 1
        code_lens[len(code.strip())] += 1
        prefixes[serial[:2].upper()] += 1

    # Run finders
    lt_candidates = find_lookup_table(pairs, min_accuracy)
    mod_candidates = find_modular(pairs, min_accuracy)

    all_candidates = lt_candidates + mod_candidates
    all_candidates.sort(key=lambda c: (-c.accuracy, -c.pairs_used))

    result = {
        "brand": brand,
        "total_pairs": len(pairs),
        "serial_length_dist": dict(serial_lens),
        "code_length_dist": dict(code_lens),
        "top_prefixes": dict(sorted(prefixes.items(), key=lambda x: -x[1])[:10]),
        "candidates": [c.to_dict() for c in all_candidates],
        "best": all_candidates[0].to_dict() if all_candidates else None,
        "lookup_table_candidates": len(lt_candidates),
        "modular_candidates": len(mod_candidates),
    }

    return result


# ─────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────

def main():
    import argparse, csv, json

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    ap = argparse.ArgumentParser(description="BluePill — Blaupunkt BP Algorithm Analyzer")
    ap.add_argument("--pairs", required=True, help="CSV file with brand,serial,code columns")
    ap.add_argument("--brand", default="blaupunkt", help="Brand name")
    ap.add_argument("--min-accuracy", type=float, default=0.85, help="Minimum accuracy threshold")
    ap.add_argument("--output", help="Output JSON file")
    args = ap.parse_args()

    # Load pairs
    csv_path = Path(args.pairs)
    pairs = []
    if csv_path.suffix == ".json":
        data = json.loads(csv_path.read_text())
        pairs = [(d["serial"], d["code"]) for d in data]
    else:
        for row in csv.DictReader(csv_path.open()):
            if row.get("serial") and row.get("code"):
                pairs.append((row["serial"], row["code"]))

    logger.info(f"Loaded {len(pairs)} pairs from {csv_path}")

    result = analyze_pairs(pairs, args.brand, args.min_accuracy)

    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2))
        logger.info(f"Results → {args.output}")
    else:
        print(json.dumps(result, indent=2))

    # Print best candidate
    if result["best"]:
        b = result["best"]
        print(f"\n✅ Best candidate: {b['name']}")
        print(f"   Accuracy: {b['accuracy']*100:.1f}% ({b['pairs_used']} pairs)")
        print(f"   Type: {b['formula_type']}")
        print(f"   {b['description']}")
    else:
        print("\n❌ No candidates found above threshold")


if __name__ == "__main__":
    main()
