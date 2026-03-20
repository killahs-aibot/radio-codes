# -*- coding: utf-8 -*-
"""Vauxhall / Opel radio code algorithm. Serial: 4 chars → Code: 4 digits."""
from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

class VauxhallAlgorithm(BaseRadioAlgorithm):
    brand_name = "Vauxhall / Opel"
    supported_models = ["CDX", "CDC", "Navi", "CDR500", "ASTRA", "VECTRA"]
    code_length = 4
    serial_pattern = r"^[A-Z0-9]{4,6}$"
    serial_format_hint = "4-6 characters on the radio label (e.g. A1234)"
    serial_location = (
        "1. Remove radio and look for label with serial\n"
        "2. Or: Enter 0000 and the serial may display\n"
        "3. Or: Check vehicle service history documents"
    )

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        if len(serial) < 4 or len(serial) > 6:
            return False, "Serial must be 4-6 characters"
        return True, None

    def calculate(self, serial: str) -> str:
        """Vauxhall algorithm."""
        serial = self.format_serial(serial)
        # Convert each character to numeric value
        total = 0
        for i, c in enumerate(serial):
            if c.isdigit():
                val = int(c)
            else:
                val = ord(c) - ord('A') + 1
            total += val * (i + 1)
        return f"{(total * 3 + 1111) % 10000:04d}"
