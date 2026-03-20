# -*- coding: utf-8 -*-
"""
VW / Audi / Seat / Skoda RCD radio code algorithm.

CONFIRMED ALGORITHM: No public formula exists.
The VW RCD security algorithm is proprietary and has NOT been publicly reversed.

Instead, we use a lookup table of known serial→code mappings collected from:
- VW Vortex forum community contributions (158 entries)
- Service records and forum posts

If a serial is not in the lookup table, the tool will show a message
suggesting the user search forums or EEPROM-read the radio.

For EEPROM reading:
1. Remove radio from vehicle
2. Locate the 24Cxx serial EEPROM chip
3. Read it with a CH341A programmer + flashrom
4. The 4-digit code is stored at a specific address

Serial format: 14-character alphanumeric (e.g. VWZ5Z7B5013069)
Supported prefixes: VWZ, AUZ, 7M0, 7L0, etc.
"""

from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

try:
    from .vw_rcd_lookup import VW_CODES
except ImportError:
    VW_CODES = {}


def _vw_calculate(serial: str) -> str:
    """
    Calculate VW RCD code from serial using lookup table.

    If the exact serial is not found, returns None and the caller
    should suggest EEPROM reading or forum lookup.
    """
    serial = serial.upper()
    serial = serial.replace("-", "").replace(" ", "")

    # Direct match
    if serial in VW_CODES:
        return VW_CODES[serial]

    # Try with VWZ prefix variation
    if not serial.startswith("VWZ") and not serial.startswith("AUZ"):
        return None

    return None


class VWRCDAlgorithm(BaseRadioAlgorithm):
    brand_name = "VW / Audi / Seat"
    supported_models = [
        "RCD210", "RCD310", "RCD510",
        "Chorus", "Concert", "Symphony",
        "Bolero", "Amundsen", "Swing",
        "MQB Radio"
    ]
    code_length = 4
    serial_pattern = r"^(?:VWZ|AUZ|[0-9A-Z]{3})[0-9A-Z]{11}$"
    serial_format_hint = "14 characters (e.g. VWZ5Z7B5013069)"
    serial_location = (
        "OPTION 1 — On the radio display:\n"
        "  Turn radio on — it shows 'SAFE'\n"
        "  Hold FM2 + SCAN buttons together until serial appears\n\n"
        "OPTION 2 — On the radio label:\n"
        "  Remove radio from dash\n"
        "  Look for label with 14-char serial (starts VWZ or AUZ)\n\n"
        "OPTION 3 — EEPROM:\n"
        "  Read the 24Cxx EEPROM with a CH341A programmer\n"
        "  The 4-digit code is stored at a known address"
    )

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        serial = serial.replace("-", "").replace(" ", "")

        # Accept VWZ and AUZ prefixed serials
        if len(serial) == 14:
            return True, None
        if len(serial) < 10:
            return False, f"Serial too short ({len(serial)} chars). Expected 14 characters."
        return True, None  # Be permissive

    def calculate(self, serial: str) -> str:
        serial = self.format_serial(serial)
        code = _vw_calculate(serial)
        if code:
            return code

        # Build helpful error message
        raise ValueError(
            f"Serial {serial} not found in local database.\n\n"
            "VW algorithm is proprietary — no free online formula exists.\n"
            "Try:\n"
            "  1. Search forums (vwvortex.com) for your serial\n"
            "  2. EEPROM read the radio with CH341A + 24Cxx chip\n"
            "  3. Pay for a code online (avoid if possible)"
        )

    def calculate_safe(self, serial: str):
        """Override to provide helpful message on lookup failure."""
        from .base import RadioInfo
        is_valid, error = self.validate_serial(serial)
        if not is_valid:
            return RadioInfo(
                brand=self.brand_name,
                model=self.supported_models[0],
                serial=serial,
                code="",
                is_valid=False,
                error_message=error,
            )
        try:
            code = self.calculate(serial)
            return RadioInfo(
                brand=self.brand_name,
                model=self.supported_models[0],
                serial=serial,
                code=code,
                is_valid=True,
            )
        except ValueError as e:
            return RadioInfo(
                brand=self.brand_name,
                model=self.supported_models[0],
                serial=serial,
                code="",
                is_valid=False,
                error_message=str(e),
            )
