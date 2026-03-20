# -*- coding: utf-8 -*-
"""Peugeot / Citroen radio code algorithm."""
from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

class PeugeotAlgorithm(BaseRadioAlgorithm):
    brand_name = "Peugeot / Citroën"
    supported_models = ["RT3", "RT4", "RNEG", "MyWay", "WipNav", "WipCom"]
    code_length = 4
    serial_pattern = r"^[A-Z0-9]{4,6}$"
    serial_format_hint = "4-6 characters on radio label (e.g. 1234AB)"
    serial_location = (
        "RT3/RT4: Press SETUP repeatedly until serial is shown.\n"
        "Or remove radio and check label on casing."
    )

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        if len(serial) < 4 or len(serial) > 6:
            return False, "Serial must be 4-6 characters"
        return True, None

    def calculate(self, serial: str) -> str:
        """Peugeot/Citroen algorithm."""
        serial = self.format_serial(serial)
        total = 0
        for i, c in enumerate(serial):
            if c.isdigit():
                val = int(c)
            else:
                val = ord(c) - ord('A') + 7
            total += val << (i * 2)
        return f"{((total ^ 0x1357) + 5000) % 10000:04d}"
