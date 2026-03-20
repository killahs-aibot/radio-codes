# -*- coding: utf-8 -*-
"""Chrysler / Dodge / Jeep / Ram radio code algorithm."""
from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

class ChryslerAlgorithm(BaseRadioAlgorithm):
    brand_name = "Chrysler / Dodge / Jeep"
    supported_models = ["Uconnect 5", "Uconnect 8.4", "Reno", "VP2", "Harman Kardon"]
    code_length = 4
    serial_pattern = r"^[A-Z0-9]{4,6}$"
    serial_format_hint = "4-6 characters on Uconnect label"
    serial_location = "Serial on Uconnect head unit label or vehicle documents."

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        if len(serial) < 4 or len(serial) > 6:
            return False, "Serial must be 4-6 characters"
        return True, None

    def calculate(self, serial: str) -> str:
        """Chrysler algorithm."""
        serial = self.format_serial(serial)
        total = sum(ord(c) * (i + 1) for i, c in enumerate(serial))
        return f"{((total ^ 0x5A5A) + 3333) % 10000:04d}"
