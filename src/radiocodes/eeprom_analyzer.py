# -*- coding: utf-8 -*-
"""
RadioUnlock EEPROM Analyzer.
Loads a radio EEPROM binary dump and extracts the unlock code.

Supported radios and their known code locations:
- 24C01/24C02/24C04 (most common 8-pin SOIC chips)
- Code is typically stored as plain 4-digit BCD at a known address per manufacturer

This tool searches common code locations and highlights potential codes.
"""

import re
import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CodeMatch:
    address: int
    code: str
    chip_name: str
    confidence: str  # "high" / "medium" / "low"


# Known code storage addresses by radio model
# address = byte offset in the EEPROM dump
# format = how the code is stored (BCD=plain digits, inverted=reversed digits)

CODE_LOCATIONS = {
    # Blaupunkt / GM cars (Opel/Vauxhall)
    "Blaupunkt CAR2003": {
        "chip": "24C02",
        "locations": [
            {"addr": 0x00, "format": "bcd", "confidence": "high", "notes": "Primary code location"},
            {"addr": 0x10, "format": "bcd", "confidence": "medium", "notes": "Backup location"},
            {"addr": 0x20, "format": "bcd", "confidence": "medium", "notes": ""},
            {"addr": 0x30, "format": "bcd", "confidence": "low", "notes": ""},
        ],
    },
    "Blaupunkt CAR2004": {
        "chip": "24C02",
        "locations": [
            {"addr": 0x00, "format": "bcd", "confidence": "high", "notes": "Primary code location"},
            {"addr": 0x08, "format": "bcd", "confidence": "high", "notes": ""},
            {"addr": 0x10, "format": "bcd", "confidence": "medium", "notes": ""},
        ],
    },
    "Blaupunkt CAR300": {
        "chip": "24C04",
        "locations": [
            {"addr": 0x00, "format": "bcd", "confidence": "high", "notes": "Primary code location"},
            {"addr": 0x10, "format": "bcd", "confidence": "medium", "notes": ""},
            {"addr": 0x20, "format": "bcd", "confidence": "low", "notes": ""},
        ],
    },
    "Blaupunkt CD300": {
        "chip": "24C04",
        "locations": [
            {"addr": 0x00, "format": "bcd", "confidence": "high", "notes": "Primary code location"},
            {"addr": 0x18, "format": "bcd", "confidence": "high", "notes": ""},
            {"addr": 0x30, "format": "bcd", "confidence": "medium", "notes": ""},
        ],
    },
    # Siemens VDO (Opel/Vauxhall)
    "Siemens VDO CR500": {
        "chip": "24C02",
        "locations": [
            {"addr": 0x00, "format": "bcd", "confidence": "high", "notes": ""},
            {"addr": 0x08, "format": "bcd", "confidence": "medium", "notes": ""},
        ],
    },
    # Ford radios
    "Ford 6000CD": {
        "chip": "24C02",
        "locations": [
            {"addr": 0x00, "format": "bcd", "confidence": "high", "notes": ""},
            {"addr": 0x04, "format": "bcd", "confidence": "high", "notes": ""},
            {"addr": 0x08, "format": "bcd", "confidence": "medium", "notes": ""},
            {"addr": 0x10, "format": "bcd", "confidence": "medium", "notes": ""},
        ],
    },
    "Ford M-Series": {
        "chip": "24C02",
        "locations": [
            {"addr": 0x00, "format": "bcd", "confidence": "high", "notes": ""},
            {"addr": 0x10, "format": "bcd", "confidence": "high", "notes": ""},
        ],
    },
    # Bosch Touch & Connect
    "Bosch Touch & Connect": {
        "chip": "24C64",
        "locations": [
            {"addr": 0x00, "format": "bcd", "confidence": "high", "notes": ""},
            {"addr": 0x10, "format": "bcd", "confidence": "medium", "notes": ""},
            {"addr": 0x80, "format": "bcd", "confidence": "medium", "notes": ""},
            {"addr": 0x100, "format": "bcd", "confidence": "low", "notes": ""},
        ],
    },
    # Renault
    "Renault": {
        "chip": "24C02",
        "locations": [
            {"addr": 0x00, "format": "bcd", "confidence": "high", "notes": ""},
            {"addr": 0x04, "format": "bcd", "confidence": "high", "notes": ""},
            {"addr": 0x08, "format": "bcd", "confidence": "medium", "notes": ""},
            {"addr": 0x10, "format": "bcd", "confidence": "medium", "notes": ""},
        ],
    },
    # VW / Audi
    "VW RCD": {
        "chip": "24C02",
        "locations": [
            {"addr": 0x00, "format": "bcd", "confidence": "high", "notes": ""},
            {"addr": 0x10, "format": "bcd", "confidence": "high", "notes": ""},
            {"addr": 0x20, "format": "bcd", "confidence": "medium", "notes": ""},
        ],
    },
    # Nissan
    "Nissan Connect": {
        "chip": "24C64",
        "locations": [
            {"addr": 0x00, "format": "bcd", "confidence": "high", "notes": ""},
            {"addr": 0x08, "format": "bcd", "confidence": "high", "notes": ""},
            {"addr": 0x10, "format": "bcd", "confidence": "medium", "notes": ""},
            {"addr": 0x100, "format": "bcd", "confidence": "low", "notes": ""},
        ],
    },
    # Generic 4-digit BCD search (all addresses)
    "Generic (4-digit BCD)": {
        "chip": "ANY",
        "locations": [
            # Scan every byte — look for 4 consecutive BCD digits
            {"addr": -1, "format": "scan_bcd", "confidence": "low", "notes": "Scans entire chip for 4-digit BCD sequences"},
        ],
    },
}


def _is_bcd_digit(b: int) -> bool:
    """Check if a byte is a valid BCD digit (0-9 encoded as 0x00-0x09)."""
    return b <= 0x09


def _read_bcd_4(data: bytes, addr: int) -> Optional[str]:
    """Read 4 BCD digits from a specific address. Returns None if not valid BCD."""
    if addr < 0 or addr + 4 > len(data):
        return None
    chunk = data[addr:addr+4]
    # Check all 4 bytes are valid BCD digits
    if not all(_is_bcd_digit(b) for b in chunk):
        return None
    return "".join(f"{b:02d}"[-1] for b in chunk)


def _find_bcd_runs(data: bytes) -> List[CodeMatch]:
    """Scan entire chip for runs of 4+ consecutive BCD digits."""
    matches = []
    consecutive = []
    for i, b in enumerate(data):
        if _is_bcd_digit(b):
            consecutive.append((i, b))
        else:
            if len(consecutive) >= 4:
                # Extract the 4-digit sequence
                addr = consecutive[0][0]
                digits = [c[1] for c in consecutive[:4]]
                code = "".join(f"{d:02d}"[-1] for d in digits)
                # Validate it's not just noise (check surrounding area)
                if _looks_like_real_code(data, addr):
                    matches.append(CodeMatch(
                        address=addr,
                        code=code,
                        chip_name="EEPROM Dump",
                        confidence="low"
                    ))
            consecutive = []
    return matches


def _looks_like_real_code(data: bytes, addr: int, window: int = 16) -> bool:
    """
    Check if a 4-digit sequence at addr looks like a real radio code.
    Rejects sequences that are adjacent to non-printable/non-BCD data in a suspicious way.
    """
    if addr < 2 or addr + 4 + 2 > len(data):
        return False
    
    # Get surrounding bytes
    before = data[addr-2:addr]
    after = data[addr+4:addr+6]
    
    # At least one surrounding byte should also be BCD or very close
    surrounding_bcd = sum(1 for b in before + after if _is_bcd_digit(b) or b <= 0x20)
    
    return surrounding_bcd >= 2


def analyze_dump(data: bytes, radio_model: str = "Generic (4-digit BCD)") -> List[CodeMatch]:
    """
    Analyze an EEPROM dump and extract potential radio codes.
    
    Args:
        data: Raw binary EEPROM dump
        radio_model: Known radio model, or "Generic (4-digit BCD)" to scan everything
    
    Returns:
        List of CodeMatch objects, sorted by confidence (high first)
    """
    results = []

    if radio_model not in CODE_LOCATIONS:
        radio_model = "Generic (4-digit BCD)"

    config = CODE_LOCATIONS[radio_model]

    # If generic scan, do full chip scan
    if config["locations"][0].get("addr") == -1:
        return _find_bcd_runs(data)

    # Check known locations for each radio model
    for loc in config["locations"]:
        addr = loc["addr"]
        fmt = loc["format"]

        if fmt == "bcd":
            code = _read_bcd_4(data, addr)
            if code:
                results.append(CodeMatch(
                    address=addr,
                    code=code,
                    chip_name=radio_model,
                    confidence=loc["confidence"]
                ))

    # Sort by confidence then address
    order = {"high": 0, "medium": 1, "low": 2}
    results.sort(key=lambda x: (order[x.confidence], x.address))

    return results


def get_supported_models() -> List[str]:
    """Return list of supported radio models."""
    return list(CODE_LOCATIONS.keys())


def identify_chip(data: bytes) -> str:
    """Try to identify the chip size from the dump."""
    size = len(data)
    if size <= 128:
        return f"24C01 ({size} bytes)"
    elif size <= 256:
        return f"24C02 ({size} bytes)"
    elif size <= 512:
        return f"24C04 ({size} bytes)"
    elif size <= 1024:
        return f"24C08 ({size} bytes)"
    elif size <= 2048:
        return f"24C16 ({size} bytes)"
    elif size <= 8192:
        return f"24C64 ({size} bytes)"
    else:
        return f"Unknown ({size} bytes)"


def load_dump(path: str) -> bytes:
    """Load an EEPROM dump file."""
    with open(path, "rb") as f:
        return f.read()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python eeprom_analyzer.py <dump_file.bin> [radio_model]")
        print(f"\nSupported radio models:")
        for model in get_supported_models():
            print(f"  - {model}")
        print("\nExample: python eeprom_analyzer.py dump.bin 'Blaupunkt CAR2003'")
        sys.exit(1)

    path = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "Generic (4-digit BCD)"

    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)

    data = load_dump(path)
    chip = identify_chip(data)
    print(f"\n📻 EEPROM Analyzer — RadioUnlock")
    print(f"Chip identified: {chip}")
    print(f"Radio model: {model}")
    print(f"File size: {len(data)} bytes")
    print()

    matches = analyze_dump(data, model)

    if matches:
        print(f"✅ Found {len(matches)} potential code(s):\n")
        for m in matches:
            conf_emoji = {"high": "🟢", "medium": "🟡", "low": "⚪️"}.get(m.confidence, "⚪️")
            print(f"  {conf_emoji} Address 0x{m.address:04X} → Code: {m.code}")
            print(f"     Confidence: {m.confidence} | Radio: {m.chip_name}")
            print()
    else:
        print("❌ No codes found.")
        print("\nTry 'Generic (4-digit BCD)' scan to search the entire dump.")
        print("Also check:\n  - Is this the correct EEPROM chip?")
        print("  - Is the dump corrupted or partial?")
        print("  - Try another radio model profile.")
