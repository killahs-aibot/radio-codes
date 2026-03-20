# -*- coding: utf-8 -*-
"""
Vauxhall / Opel Radio Code Algorithm.

STATUS: LOOKUP DATABASE (growing)

Different radio manufacturers = different serial formats and algorithms:
- Blaupunkt CAR2003: serial GM0203xxxxxxxx → forum lookup (17 pairs)
- Blaupunkt CAR300: serial GM030Mxxxxxxxxx → forum lookup
- Blaupunkt CAR400: serial GM0400xxxxxxx → forum lookup
- Delphi CAR2004: serial GM0204xx, GM0670, GM0804, GM1670, GM1681 → forum pairs
- Siemens SC804: serial GM0804xxxx → forum pairs
- Bosch Touch & Connect: serial CM0141xxxxxxxxx → VIN-linked, no algo

Forum lookup covers: opel, vauxhall, blaupunkt brands.

Serial formats: GM0203..., GM0204..., GM030M..., GM0400..., GM0804..., CM0141...
"""

from typing import Tuple, Optional
from .base import BaseRadioAlgorithm, RadioInfo


class VauxhallAlgorithm(BaseRadioAlgorithm):
    brand_name = "Vauxhall / Opel"
    supported_models = [
        "CAR2003 (Blaupunkt)",
        "CAR2004 (Delphi)",
        "CAR300 (Blaupunkt)",
        "CAR400 (Blaupunkt)",
        "SC804 (Siemens)",
        "CD30 MP3",
        "CD70 Navi",
        "Touch & Connect (Bosch) — VIN lookup required",
    ]
    code_length = 4
    serial_pattern = r"^(GM0[0-9]{8,}|CM01[0-9]{7,}|22DC[0-9]{3}.*)$"
    serial_format_hint = "Serial starts GM0... or CM01... (e.g. GM020328268659)"
    serial_location = (
        "OPTION 1 — On the radio label:\n"
        "  Remove radio from dashboard\n"
        "  Serial is printed on label (starts GM0 or CM01)\n\n"
        "OPTION 2 — From locked radio display:\n"
        "  Enter wrong code 3 times\n"
        "  Serial may appear on screen\n\n"
        "OPTION 3 — EEPROM read (for ALL models):\n"
        "  Remove radio and locate 24Cxx EEPROM chip\n"
        "  Read with CH341A programmer + flashrom\n"
        "  Code stored at known address per model"
    )

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = serial.upper().replace(" ", "").replace("-", "")
        if len(serial) < 8:
            return False, f"Serial too short ({len(serial)} chars)"
        return True, None

    def calculate(self, serial: str) -> str:
        serial = serial.upper().replace(" ", "").replace("-", "")

        # Try prefix lookup (brand 'opel' and 'vauxhall' and 'blaupunkt')
        for brand in ("opel", "vauxhall", "blaupunkt"):
            result = self._prefix_lookup(brand, serial)
            if result:
                return result

        raise ValueError(
            f"Serial {serial} not found in local database.\n\n"
            "Vauxhall/Opel uses multiple radio manufacturers (Blaupunkt, Delphi, Bosch).\n"
            "Database has 17 known pairs for GM0xxx serials — enter a known prefix.\n"
            "For EEPROM read: CH341A programmer + 24Cxx chip = free for any model."
        )

    def _prefix_lookup(self, brand: str, serial: str) -> Optional[str]:
        """Try to find code via prefix match in forum_pairs.csv."""
        try:
            from ..lookup_engine import lookup, prefix_lookup
            # Try exact first
            r = lookup(brand, serial)
            if r:
                return r["code"]
            # Try prefix
            r = prefix_lookup(brand, serial, min_length=8)
            if r:
                return r["code"]
        except Exception:
            pass
        return None

    def calculate_safe(self, serial: str) -> RadioInfo:
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
