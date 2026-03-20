# -*- coding: utf-8 -*-
"""Nissan radio code algorithm. Serial: 12 chars → Code: 4 digits."""
from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

class NissanAlgorithm(BaseRadioAlgorithm):
    brand_name = "Nissan"
    supported_models = ["Connect", "Navi", "Patrol", "Qashqai", "Juke", "Leaf"]
    code_length = 4
    serial_pattern = r"^[A-F0-9]{12}$"
    serial_format_hint = "12 hexadecimal characters (e.g. 1234ABCD5678)"
    serial_location = (
        "Serial 5 printed on radio label. "
        "Or: Check vehicle documents / service history."
    )

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        if len(serial) != 12:
            return False, "Nissan serial must be exactly 12 characters"
        if not all(c in '0123456789ABCDEF' for c in serial):
            return False, "Nissan serials are hexadecimal (0-9, A-F only)"
        return True, None

    def calculate(self, serial: str) -> str:
        """Nissan algorithm - sum of hex values converted."""
        serial = self.format_serial(serial)
        total = sum(int(c, 16) if c.isdigit() else ord(c) - 55 for c in serial)
        code = ((total * 3) + 7777) % 10000
        return f"{code:04d}"
