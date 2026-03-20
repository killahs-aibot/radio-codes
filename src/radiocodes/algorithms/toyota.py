# -*- coding: utf-8 -*-
"""Toyota / Lexus ERC radio code algorithm. Serial: 16 chars → Code: 5 digits."""
from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

class ToyotaAlgorithm(BaseRadioAlgorithm):
    brand_name = "Toyota / Lexus"
    supported_models = ["ERC", "Touch", "Entune", "Lexus Nav"]
    code_length = 5
    serial_pattern = r"^[A-Z0-9]{16}$"
    serial_format_hint = "16-character ERC code on radio label"
    serial_location = (
        "ERC code printed on radio label. "
        "Or: Check in vehicle settings > about > radio."
    )

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        if len(serial) != 16:
            return False, "Toyota ERC code must be exactly 16 characters"
        return True, None

    def calculate(self, serial: str) -> str:
        """Toyota ERC algorithm - awaiting research confirmation."""
        serial = self.format_serial(serial)
        raise NotImplementedError("Toyota ERC algorithm pending Tam research.")
