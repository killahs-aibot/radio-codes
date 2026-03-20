# -*- coding: utf-8 -*-
"""Alfa Romeo radio code algorithm. Similar to Fiat."""
from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

class AlfaAlgorithm(BaseRadioAlgorithm):
    brand_name = "Alfa Romeo"
    supported_models = ["Connect", "Nav+", "Giulietta", "Mito", "Giulia"]
    code_length = 4
    serial_pattern = r"^[A-F0-9]{4,6}$"
    serial_format_hint = "4-6 hex characters on label"
    serial_location = "Serial printed on radio label on casing."

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        if len(serial) < 4 or len(serial) > 6:
            return False, "Serial must be 4-6 characters"
        return True, None

    def calculate(self, serial: str) -> str:
        """Alfa Romeo - same family as Fiat, similar algorithm."""
        serial = self.format_serial(serial)
        val = int(serial, 16)
        code = ((val * 9) + 0x1F3D) & 0xFFFF
        return f"{code % 10000:04d}"
