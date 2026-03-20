# -*- coding: utf-8 -*-
"""Ford V Series radio code algorithm. Serial: 6 digits → Code: 4 digits."""
from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

class FordVAlgorithm(BaseRadioAlgorithm):
    brand_name = "Ford"
    supported_models = ["V Series", "V Serial", "TravelPilot"]
    code_length = 4
    serial_pattern = r"^\d{6}$"
    serial_format_hint = "6 digits (e.g. 123456)"
    serial_location = "Serial displayed on radio screen or on label on casing"

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        if len(serial) != 6:
            return False, "Serial must be exactly 6 digits"
        if not serial.isdigit():
            return False, "Serial must contain only digits"
        return True, None

    def calculate(self, serial: str) -> str:
        serial = self.format_serial(serial)
        raise NotImplementedError("Ford V Series algorithm pending Tam research.")
