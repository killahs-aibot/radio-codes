# -*- coding: utf-8 -*-
"""
Serial auto-detection for radio codes.

Given a serial number, figure out which brand/algorithm it belongs to.
Run this before showing the brand dropdown — auto-select the most likely brand.
"""

import re
from typing import Optional, Tuple

# Serial format patterns for each brand
# Evaluated IN ORDER — first match wins
# (regex pattern, brand key, confidence: 0-1)
SERIAL_PATTERNS = [
    # Ford V-Series BEFORE generic M/V (must check V first)
    (r"^V\d{6}$", "Ford V-Series", 0.98),

    # Ford M-Series: M + 6 digits (but NOT V)
    (r"^M\d{6}$", "Ford M-Series", 0.98),

    # Ford Figo: VCOOAB + 8 digits (e.g. VCOOAB12345678)
    (r"^VCOOAB\d{8}$", "Ford Figo", 0.98),

    # Ford EcoSport: ABC + 6 digits (e.g. ABC123456)
    (r"^ABC\d{6}$", "Ford EcoSport", 0.98),

    # Ford SONY CD: SOCD + alphanumeric (e.g. SOCD123V456789, 13+ chars)
    (r"^SOCD[0-9A-Z]{5,}$", "Ford SONY CD", 0.98),

    # Ford Blaupunkt: BP + alphanumeric (e.g. BP8203X1234567)
    (r"^BP[0-9A-Z]{6,}$", "Ford Blaupunkt", 0.90),

    # Ford TravelPilot: 8-char hex-like (e.g. A1B2C3D4)
    (r"^[A-F0-9]{8}$", "Ford TravelPilot", 0.85),

    # Ford Sanyo: 12 digits (e.g. 123456789012)
    (r"^\d{12}$", "Ford Sanyo", 0.75),

    # Kia: letter A-H + 3 digits (comes before Renault which is also letter+3digits)
    (r"^[A-Ha-h]\d{3}$", "Kia", 0.85),

    # Renault: letter + 3 digits (e.g. D123, T456) — but NOT A-H which is Kia
    (r"^[A-Za-h]\d{3}$", "Renault / Dacia", 0.80),
    # Renault also: full precode like "D123" (uppercase)
    (r"^[I-Zi-z]\d{3}$", "Renault / Dacia", 0.80),

    # Blaupunkt BP: starts with BP followed by digits/letters
    (r"^BP\d{10,}$", "Blaupunkt", 0.95),
    (r"^BP\d+[A-Z0-9]*$", "Blaupunkt", 0.75),

    # VW 14-char: VWZ5Z7B5013069, etc.
    (r"^VW[Zz]\d[A-Za-z]\d[A-Za-z0-9]{8,12}$", "VW / Audi / Seat / Skoda", 0.98),

    # BMW
    (r"^WBA[0-9A-Fa-f]{12}$", "BMW", 0.98),

    # Porsche
    (r"^WP0[0-9A-Z]{12}$", "Porsche", 0.98),

    # Opel/GM: GM0xxx format
    (r"^GM0[0-9]{6,}$", "Vauxhall / Opel", 0.95),
    (r"^GM0[0-9]{3}$", "Vauxhall / Opel", 0.95),
    (r"^GM0[0-9]{4}$", "Vauxhall / Opel", 0.95),

    # Fiat VP1/VP2
    (r"^VP[12]-[A-Z0-9-]+$", "Fiat / Alfa Romeo", 0.98),

    # Fiat VP1/VP2 last 4 digits
    (r"^\d{4}$", "Fiat / Alfa Romeo", 0.40),

    # Nissan: 12-char alphanumeric
    (r"^[A-Z0-9]{12}$", "Nissan", 0.70),

    # Honda: various formats
    (r"^3V3[A-Z0-9-]+$", "Honda", 0.95),
    (r"^[A-HJ-NP-Z0-9]{5,10}$", "Honda", 0.35),

    # Peugeot/Citroen
    (r"^\d{4}[A-Z0-9]{6,}$", "Peugeot", 0.60),

    # 6 digits → likely Ford M/V without prefix
    (r"^\d{6}$", "Ford M-Series", 0.30),
]


def detect_brand(serial: str) -> Tuple[Optional[str], float]:
    """
    Auto-detect the car brand from a radio serial number.

    Args:
        serial: The serial number string (will be stripped and uppercased)

    Returns:
        Tuple of (brand_key, confidence) or (None, 0.0) if no match.
        Confidence is 0.0-1.0.
    """
    s = serial.strip().upper()

    for pattern, brand, confidence in SERIAL_PATTERNS:
        if re.match(pattern, s):
            return brand, confidence

    return None, 0.0


def get_format_hint(serial: str) -> str:
    """Get a human-readable format hint for the serial."""
    s = serial.strip()
    length = len(s)
    hints = {
        3: "3-char serials may be Renault precode (letter+2 digits)",
        4: "4-digit serials are often Fiat/Alfa VP1/VP2 (enter last 4 digits of serial)",
        5: "5-digit serials may be Honda or similar",
        6: "6-digit serials without a prefix may be Ford M/V series (try adding M or V prefix)",
        7: "7-char serials (letter + 6 digits) are typically Ford M or V series",
        8: "8-char hex-like serials may be Ford TravelPilot (e.g. A1B2C3D4)",
        12: "12-digit serials may be Ford Sanyo (12 consecutive digits)",
        13: "13-char serials starting with SOCD may be Ford SONY CD format",
        14: "14-char serial: VW/Audi/Skoda/Seat (VWZ) or Ford Figo (VCOOAB prefix)",
        15: "15-char serials — check if prefix matches a known format",
    }
    if length in hints:
        return hints[length]
    if length > 14:
        return "Long serial — may be VW/Audi or similar premium brand"
    return f"Serial length: {length} characters"


# Quick self-test
if __name__ == "__main__":
    test_serials = [
        "M025345", "V007337", "D123", "H050",
        "VWZ5Z7B5013069", "GM020328268659",
        "VP1-1234", "123456789012", "1234",
        "BP234631991366", "7D2F", "123456",
        "GM0203", "C123", "T456",
        # New Ford formats
        "VCOOAB12345678", "ABC123456", "SOCD123V456789",
        "BP8203X1234567", "A1B2C3D4", "123456789012",
    ]
    print("Serial Auto-Detection Tests:")
    for serial in test_serials:
        brand, conf = detect_brand(serial)
        hint = get_format_hint(serial)
        print(f"  {serial:25s} -> {brand or 'Unknown':30s} ({conf:.0%}) | {hint}")
