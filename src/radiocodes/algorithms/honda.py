# -*- coding: utf-8 -*-
"""Honda radio code algorithm. Serial: 5-10 chars → Code: 5 digits."""
from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

class HondaAlgorithm(BaseRadioAlgorithm):
    brand_name = "Honda"
    supported_models = ["Civic", "Accord", "CR-V", "Jazz", "HR-V", "Fit"]
    code_length = 5
    serial_pattern = r"^[A-Z0-9]{5,10}$"
    serial_format_hint = "5-10 characters on radio label (e.g. A12345)"
    serial_location = (
        "Serial on label on the radio casing. "
        "Or: Check vehicle documents / registration."
    )

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        if len(serial) < 5 or len(serial) > 10:
            return False, "Honda serial must be 5-10 characters"
        return True, None

    def calculate(self, serial: str) -> str:
        """Honda algorithm - awaiting research confirmation."""
        serial = self.format_serial(serial)
        raise NotImplementedError("Honda algorithm pending Tam research confirmation.")
