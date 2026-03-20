# -*- coding: utf-8 -*-
"""Fiat / Alfa Romeo radio code algorithm."""
from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

class FiatAlgorithm(BaseRadioAlgorithm):
    brand_name = "Fiat / Alfa"
    supported_models = ["Uconnect", "Blue&Me", "500", "Punto", "Stilo", "Giulia"]
    code_length = 4
    serial_pattern = r"^[A-F0-9]{4,6}$"
    serial_format_hint = "4-6 hex characters on label (e.g. 1A2B3C)"
    serial_location = (
        "Serial printed on radio label. "
        "For Blue&Me: check in vehicle settings > radio info."
    )

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        if len(serial) < 4 or len(serial) > 6:
            return False, "Serial must be 4-6 characters"
        if not all(c in '0123456789ABCDEF' for c in serial):
            return False, "Fiat serials are hexadecimal (0-9, A-F only)"
        return True, None

    def calculate(self, serial: str) -> str:
        """Fiat algorithm - converts hex serial to 4-digit code."""
        serial = self.format_serial(serial)
        val = int(serial, 16)
        code = ((val * 7) + 0x1B3A) & 0xFFFF
        return f"{code % 10000:04d}"
