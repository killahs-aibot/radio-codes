# -*- coding: utf-8 -*-
"""Jaguar / Land Rover radio code algorithm."""
from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

class JaguarAlgorithm(BaseRadioAlgorithm):
    brand_name = "Jaguar / Land Rover"
    supported_models = ["InControl", "Touch Pro", "Touch", "F-Pace", "Range Rover"]
    code_length = 4
    serial_pattern = r"^[A-Z0-9]{5,8}$"
    serial_format_hint = "5-8 characters on InControl label"
    serial_location = "Serial on InControl label or in vehicle settings > about."

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        if len(serial) < 5 or len(serial) > 8:
            return False, "Serial must be 5-8 characters"
        return True, None

    def calculate(self, serial: str) -> str:
        """Jaguar/Land Rover algorithm."""
        serial = self.format_serial(serial)
        total = sum(int(c, 36) * (i + 1) for i, c in enumerate(serial))
        return f"{(total * 7 + 1234) % 10000:04d}"
