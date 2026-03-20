# -*- coding: utf-8 -*-
"""⚠️  UNVERIFIED — Alfa Romeo radio code algorithm.

STATUS: UNVERIFIED — No publicly confirmed formula.
        May produce WRONG codes. USE WITH CAUTION.

Alfa Romeo radios often share architecture with Fiat (VP1/VP2).
Try Fiat algorithm first for Blaupunkt-based units.

For guaranteed correct codes: EEPROM reading recommended.
"""
from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

class AlfaAlgorithm(BaseRadioAlgorithm):
    brand_name = "Alfa Romeo ⚠️ UNVERIFIED"
    supported_models = ["Blaupunkt", "Navi", "Connect"]
    code_length = 4
    serial_pattern = r"^[A-Z0-9]{4,20}$"
    serial_format_hint = "Serial on radio label (Blaupunkt BP... format)"
    serial_location = "Remove radio, check label on top/side. Or try Fiat VP1/VP2 algorithm."
    verified = False  # 🔴 NOT VERIFIED

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        return True, None

    def calculate(self, serial: str) -> str:
        """⚠️ UNVERIFIED — Try Fiat VP1/VP2 algorithm for Blaupunkt units.
        
        Alfa Romeo shares platforms with Fiat. For BP... serials,
        the Fiat algorithm may work. Try both and compare.
        """
        serial = self.format_serial(serial)
        # Placeholder — no verified formula
        raise NotImplementedError(
            "Alfa Romeo: No verified algorithm found. "
            "Try Fiat VP1/VP2 for Blaupunkt units, "
            "or use EEPROM Reader for guaranteed extraction."
        )
