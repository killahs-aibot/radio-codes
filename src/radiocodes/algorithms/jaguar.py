# -*- coding: utf-8 -*-
"""⚠️  UNVERIFIED — Jaguar / Land Rover radio code algorithm.

STATUS: UNVERIFIED — No publicly confirmed formula.
        May produce WRONG codes. USE WITH CAUTION.

Jaguar/Land Rover codes are often printed on a security card
in the glovebox. The code may also be flash-coded to the cluster.

For guaranteed correct codes: EEPROM reading recommended.
"""
from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

class JaguarAlgorithm(BaseRadioAlgorithm):
    brand_name = "Jaguar / Land Rover ⚠️ UNVERIFIED"
    supported_models = ["RSE", "RVC", "ICT", "InControl"]
    code_length = 4
    serial_pattern = r"^[A-Z0-9]{4,20}$"
    serial_format_hint = "Serial on radio label or vehicle documents"
    serial_location = "Check glovebox security card or vehicle documents"
    verified = False  # 🔴 NOT VERIFIED

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        return True, None

    def calculate(self, serial: str) -> str:
        """⚠️ UNVERIFIED — no confirmed formula exists."""
        serial = self.format_serial(serial)
        raise NotImplementedError(
            "Jaguar/Land Rover: No verified algorithm found. "
            "Use EEPROM Reader for guaranteed code extraction."
        )
