# -*- coding: utf-8 -*-
"""
RadioUnlock EEPROM Dump Analyzer v2.
Loads a radio EEPROM binary dump and extracts unlock codes.

Supported chips: 24C01 · 24C02 · 24C04 · 24C08 · 24C16 · 24C64
Supported radios: Blaupunkt, Ford, Opel/Vauxhall, Renault, VW, Nissan, Honda, etc.

Usage:
  python3 -m radiocodes.eeprom_analyzer dump.bin [model]

  # Scan entire dump for 4-digit BCD codes
  python3 -m radiocodes.eeprom_analyzer dump.bin --scan

  # Scan with a specific radio model
  python3 -m radiocodes.eeprom_analyzer dump.bin "Blaupunkt CAR2003"
"""

import sys
import os
from dataclasses import dataclass
from typing import List, Optional, Tuple

# ── Chip definitions ────────────────────────────────────────────────────────

CHIP_SIZES = {
    "24C01": 128,
    "24C02": 256,
    "24C04": 512,
    "24C08": 1024,
    "24C16": 2048,
    "24C64": 8192,
}

# Known code storage locations by radio model.
# addr = byte offset in EEPROM. -1 means scan entire chip.
# fmt = "bcd" (digits 0-9 stored as 0x00-0x09) or "ascii"
RADIO_LOCATIONS = {
    # ── Blaupunkt / Opel ──────────────────────────────────────────────
    "Blaupunkt CAR2003": {
        "chip": "24C02",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x08, "confidence": "high"},
            {"addr": 0x10, "confidence": "medium"},
            {"addr": 0x18, "confidence": "medium"},
            {"addr": 0x20, "confidence": "low"},
            {"addr": 0x30, "confidence": "low"},
        ],
    },
    "Blaupunkt CAR2004": {
        "chip": "24C02",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x08, "confidence": "high"},
            {"addr": 0x10, "confidence": "medium"},
            {"addr": 0x18, "confidence": "medium"},
        ],
    },
    "Blaupunkt CAR300": {
        "chip": "24C04",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x08, "confidence": "high"},
            {"addr": 0x10, "confidence": "medium"},
            {"addr": 0x18, "confidence": "medium"},
            {"addr": 0x80, "confidence": "low"},
        ],
    },
    "Blaupunkt CD300": {
        "chip": "24C04",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x08, "confidence": "high"},
            {"addr": 0x10, "confidence": "medium"},
            {"addr": 0x18, "confidence": "medium"},
            {"addr": 0x80, "confidence": "low"},
        ],
    },
    "Blaupunkt PC2003": {
        "chip": "24C02",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x10, "confidence": "high"},
            {"addr": 0x20, "confidence": "medium"},
        ],
    },
    "Blaupunkt PC5004": {
        "chip": "24C02",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x08, "confidence": "high"},
            {"addr": 0x10, "confidence": "medium"},
        ],
    },
    # ── Opel / Vauxhall ───────────────────────────────────────────────
    "Opel / Vauxhall CDX": {
        "chip": "24C02",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x08, "confidence": "high"},
            {"addr": 0x10, "confidence": "medium"},
        ],
    },
    "Opel / Vauxhall CDC": {
        "chip": "24C02",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x10, "confidence": "high"},
            {"addr": 0x20, "confidence": "medium"},
        ],
    },
    "Opel / Vauxhall Navi": {
        "chip": "24C04",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x08, "confidence": "high"},
            {"addr": 0x80, "confidence": "medium"},
        ],
    },
    # ── Ford ─────────────────────────────────────────────────────────
    "Ford 6000CD": {
        "chip": "24C02",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x04, "confidence": "high"},
            {"addr": 0x08, "confidence": "medium"},
            {"addr": 0x10, "confidence": "medium"},
            {"addr": 0x20, "confidence": "low"},
        ],
    },
    "Ford M-Series": {
        "chip": "24C02",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x10, "confidence": "high"},
            {"addr": 0x20, "confidence": "medium"},
        ],
    },
    "Ford TravelPilot": {
        "chip": "24C02",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x08, "confidence": "high"},
            {"addr": 0x10, "confidence": "medium"},
        ],
    },
    # ── Renault ──────────────────────────────────────────────────────
    "Renault / Dacia": {
        "chip": "24C02",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x04, "confidence": "high"},
            {"addr": 0x08, "confidence": "medium"},
            {"addr": 0x10, "confidence": "medium"},
        ],
    },
    # ── VW / Audi ────────────────────────────────────────────────────
    "VW RCD 300": {
        "chip": "24C02",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x10, "confidence": "high"},
            {"addr": 0x20, "confidence": "medium"},
            {"addr": 0x30, "confidence": "low"},
        ],
    },
    "VW RCD 310": {
        "chip": "24C02",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x08, "confidence": "high"},
            {"addr": 0x10, "confidence": "medium"},
        ],
    },
    "VW RCD 510": {
        "chip": "24C04",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x08, "confidence": "high"},
            {"addr": 0x10, "confidence": "medium"},
            {"addr": 0x80, "confidence": "low"},
        ],
    },
    "Audi Chorus / Concert / Symphony": {
        "chip": "24C02",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x10, "confidence": "high"},
            {"addr": 0x20, "confidence": "medium"},
        ],
    },
    # ── Fiat / Alfa ─────────────────────────────────────────────────
    "Fiat Uconnect": {
        "chip": "24C02",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x10, "confidence": "high"},
        ],
    },
    "Alfa Romeo Connect": {
        "chip": "24C02",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x08, "confidence": "medium"},
        ],
    },
    # ── Nissan ───────────────────────────────────────────────────────
    "Nissan Connect": {
        "chip": "24C64",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x08, "confidence": "high"},
            {"addr": 0x10, "confidence": "medium"},
            {"addr": 0x80, "confidence": "low"},
            {"addr": 0x100, "confidence": "low"},
        ],
    },
    "Nissan Patrol / Qashqai": {
        "chip": "24C64",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x10, "confidence": "high"},
            {"addr": 0x100, "confidence": "medium"},
        ],
    },
    # ── Honda ────────────────────────────────────────────────────────
    "Honda / Acura": {
        "chip": "24C02",
        "code_len": 5,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x04, "confidence": "high"},
            {"addr": 0x08, "confidence": "medium"},
            {"addr": 0x10, "confidence": "medium"},
        ],
    },
    # ── Bosch ───────────────────────────────────────────────────────
    "Bosch Touch & Connect": {
        "chip": "24C64",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x08, "confidence": "high"},
            {"addr": 0x10, "confidence": "medium"},
            {"addr": 0x80, "confidence": "medium"},
            {"addr": 0x100, "confidence": "low"},
        ],
    },
    # ── Siemens VDO ─────────────────────────────────────────────────
    "Siemens VDO CR500": {
        "chip": "24C02",
        "code_len": 4,
        "fmt": "bcd",
        "locations": [
            {"addr": 0x00, "confidence": "high"},
            {"addr": 0x08, "confidence": "high"},
            {"addr": 0x10, "confidence": "medium"},
        ],
    },
    # ── Scan all ────────────────────────────────────────────────────
    "FULL SCAN": {
        "chip": "ANY",
        "code_len": 4,
        "fmt": "scan_bcd",
        "locations": [
            {"addr": -1, "confidence": "low"},
        ],
    },
    "FULL SCAN 5-digit": {
        "chip": "ANY",
        "code_len": 5,
        "fmt": "scan_bcd",
        "locations": [
            {"addr": -1, "confidence": "low"},
        ],
    },
}


# ── Core analysis ───────────────────────────────────────────────────────────

@dataclass
class CodeMatch:
    """A potential radio code found in an EEPROM dump."""
    address: int
    code: str
    confidence: str  # "high" / "medium" / "low"
    radio: str
    notes: str = ""


def _is_bcd(b: int) -> bool:
    """Return True if byte is a valid BCD digit (0x00-0x09)."""
    return 0 <= b <= 9


def _read_bcd(data: bytes, addr: int, num_digits: int = 4) -> Optional[str]:
    """Read N BCD digits from addr. Returns None if any byte is invalid BCD."""
    if addr < 0 or addr + num_digits > len(data):
        return None
    chunk = data[addr:addr + num_digits]
    if not all(_is_bcd(b) for b in chunk):
        return None
    return "".join(f"{b:02d}"[-1] for b in chunk)


def _read_bcd_reversed(data: bytes, addr: int, num_digits: int = 4) -> Optional[str]:
    """Read N BCD digits in reverse order (some radios store LSB-first)."""
    normal = _read_bcd(data, addr, num_digits)
    if normal is None:
        return None
    return normal[::-1]


def _scan_full(data: bytes, num_digits: int = 4) -> List[CodeMatch]:
    """
    Scan the entire EEPROM dump for runs of consecutive BCD digits.
    Returns a list of potential codes.
    """
    matches = []
    i = 0
    while i <= len(data) - num_digits:
        # Try forward read
        code = _read_bcd(data, i, num_digits)
        if code:
            # Check surrounding context
            context = _assess_context(data, i, num_digits)
            if context >= 2:  # At least 2 surrounding BCD-ish bytes
                # Avoid duplicates
                dup = any(m.address == i for m in matches)
                if not dup:
                    confidence = "high" if context >= 4 else ("medium" if context >= 3 else "low")
                    matches.append(CodeMatch(
                        address=i,
                        code=code,
                        confidence=confidence,
                        radio="Unknown",
                        notes=f"context={context}"
                    ))
            i += num_digits  # Skip past this sequence
        else:
            i += 1
    return matches


def _assess_context(data: bytes, addr: int, num_digits: int, window: int = 6) -> int:
    """
    Count how many surrounding bytes look like part of a code structure.
    Higher = more likely to be a real code. Max score = 6.
    """
    score = 0
    start = max(0, addr - window)
    end = min(len(data), addr + num_digits + window)
    for j in range(start, end):
        if j < addr or j >= addr + num_digits:
            b = data[j]
            if _is_bcd(b):
                score += 1
            elif b == 0xFF or b == 0x00:
                score += 0.5
    return min(score, 6)


def analyze(data: bytes, radio_model: str = "FULL SCAN", num_digits: int = 4) -> List[CodeMatch]:
    """
    Analyze an EEPROM dump and find potential unlock codes.

    Args:
        data: Raw binary dump from the EEPROM chip
        radio_model: Specific radio model, or "FULL SCAN" / "FULL SCAN 5-digit"
        num_digits: Number of BCD digits for the code (4 or 5)

    Returns:
        List of CodeMatch sorted by confidence (high first)
    """
    if radio_model not in RADIO_LOCATIONS:
        radio_model = "FULL SCAN"

    cfg = RADIO_LOCATIONS[radio_model]
    results: List[CodeMatch] = []

    if cfg["fmt"] == "scan_bcd":
        return _scan_full(data, num_digits)

    # Check known locations
    for loc in cfg["locations"]:
        addr = loc["addr"]
        # Try normal byte order
        code = _read_bcd(data, addr, cfg["code_len"])
        # Try reversed byte order (some radios store LSB-first)
        code_rev = _read_bcd_reversed(data, addr, cfg["code_len"])

        for c, note in [(code, ""), (code_rev, " (reversed)")]:
            if c:
                # Check this isn't a duplicate
                if not any(m.address == addr and m.code == c for m in results):
                    results.append(CodeMatch(
                        address=addr,
                        code=c,
                        confidence=loc["confidence"],
                        radio=radio_model,
                        notes=note.strip()
                    ))

    # Sort: high confidence first, then by address
    order = {"high": 0, "medium": 1, "low": 2}
    results.sort(key=lambda m: (order[m.confidence], m.address))
    return results


def get_supported_models() -> List[str]:
    """Return sorted list of supported radio model names."""
    models = sorted(RADIO_LOCATIONS.keys())
    return models


def identify_chip(data: bytes) -> str:
    """Identify the EEPROM chip from its size."""
    size = len(data)
    for chip, sz in CHIP_SIZES.items():
        if size == sz:
            return f"{chip} ({sz} bytes)"
    return f"Unknown ({size} bytes)"


def load_dump(path: str) -> bytes:
    """Load an EEPROM dump file."""
    with open(path, "rb") as f:
        return f.read()


# ── Hexdump ────────────────────────────────────────────────────────────────

def hexdump(data: bytes, offset: int = 0, length: int = 256) -> str:
    """
    Generate a readable hexdump of a region of the dump.
    Shows offset, hex bytes, and ASCII representation.
    """
    end = min(offset + length, len(data))
    lines = []
    for i in range(offset, end, 16):
        chunk = data[i:i+16]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{i:04X}  {hex_part:<48}  {ascii_part}")
    return "\n".join(lines)


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("📻 EEPROM Analyzer — RadioUnlock")
        print()
        print("Usage:")
        print("  python3 -m radiocodes.eeprom_analyzer <dump.bin> [model]")
        print("  python3 -m radiocodes.eeprom_analyzer <dump.bin> --scan")
        print()
        print("Supported models:")
        print("  FULL SCAN       — Scan entire chip (all radios, all addresses)")
        print("  FULL SCAN 5-digit — For Honda 5-digit codes")
        print()
        for model in sorted(RADIO_LOCATIONS.keys()):
            if not model.startswith("FULL"):
                print(f"  {model}")
        return

    path = sys.argv[1]

    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return

    data = load_dump(path)
    chip = identify_chip(data)

    # Determine model
    if len(sys.argv) > 2:
        model_arg = sys.argv[2]
        if model_arg == "--scan":
            model = "FULL SCAN"
        elif model_arg == "--scan5":
            model = "FULL SCAN 5-digit"
        else:
            model = model_arg
            if model not in RADIO_LOCATIONS:
                print(f"⚠️  Unknown model '{model}', using FULL SCAN instead.")
                model = "FULL SCAN"
    else:
        model = "FULL SCAN"

    num_digits = 5 if "5-digit" in model else 4

    print("=" * 60)
    print("📻 EEPROM Analyzer — RadioUnlock")
    print("=" * 60)
    print(f"File:       {os.path.basename(path)}")
    print(f"Size:       {len(data):,} bytes ({chip})")
    print(f"Model:      {model}")
    print(f"Code digits: {num_digits}")
    print("=" * 60)

    matches = analyze(data, model, num_digits)

    if matches:
        # Group by confidence
        high = [m for m in matches if m.confidence == "high"]
        med = [m for m in matches if m.confidence == "medium"]
        low = [m for m in matches if m.confidence == "low"]

        print(f"\n✅ Found {len(matches)} potential code(s):\n")

        if high:
            print(f"🟢 HIGH CONFIDENCE ({len(high)}):")
            for m in high:
                print(f"   0x{m.address:04X} → {m.code}  {m.notes}")
            print()

        if med:
            print(f"🟡 MEDIUM CONFIDENCE ({len(med)}):")
            for m in med:
                print(f"   0x{m.address:04X} → {m.code}  {m.notes}")
            print()

        if low and model == "FULL SCAN":
            print(f"⚪ LOW CONFIDENCE ({len(low)}) — try a specific radio model:")
            shown = low[:10]
            for m in shown:
                print(f"   0x{m.address:04X} → {m.code}")
            if len(low) > 10:
                print(f"   ... and {len(low) - 10} more (use specific model to filter)")
            print()

        # Show hexdump around each high-confidence match
        print("-" * 60)
        print("Hexdump around HIGH confidence addresses:\n")
        for m in high[:3]:
            print(f"Address 0x{m.address:04X} (code: {m.code}):")
            start = max(0, m.address - 16)
            print(hexdump(data, start, 64))
            print()
    else:
        print("\n❌ No codes found.")
        print()
        print("Tips:")
        print("  • Make sure you dumped the correct chip (24C0x SOIC 8-pin)")
        print("  • Some radios need a FULL SCAN: --scan")
        print("  • If the chip is 24C64 (Nissan, Bosch), use specific model")
        print("  • Try another radio model from the supported list")
        print("  • The dump may be from a different chip — check the radio board")


if __name__ == "__main__":
    main()
