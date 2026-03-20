# -*- coding: utf-8 -*-
"""⚠️  UNVERIFIED — Nissan radio code algorithm.

STATUS: UNVERIFIED — This formula has NOT been publicly confirmed with test vectors.
        It may produce WRONG codes. USE WITH CAUTION.

Nissan serial format: 12 hexadecimal characters (e.g. CY16C-1234567)

NOTE: The formula below is a best-effort guess based on general patterns.
      For guaranteed correct codes, use EEPROM reading or the official
      Nissan portal: https://radio-navicode.nissan.com/

⚠️  WARNING: Do NOT trust codes from this algorithm without verification!
"""
from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

class NissanAlgorithm(BaseRadioAlgorithm):
    brand_name = "Nissan ⚠️ UNVERIFIED"
    supported_models = ["Connect", "Navi", "Patrol", "Qashqai", "Juke", "Leaf"]
    code_length = 4
    serial_pattern = r"^[A-F0-9]{12}$"
    serial_format_hint = "12 hex characters (e.g. CY16C1234567)"
    serial_location = (
        "Serial on label on the radio. "
        "Or: https://radio-navicode.nissan.com/"
    )
    verified = False  # 🔴 NOT VERIFIED — no confirmed test vectors

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        if len(serial) != 12:
            return False, "Nissan serial must be exactly 12 characters"
        if not all(c in '0123456789ABCDEF' for c in serial.upper()):
            return False, "Nissan serials are hexadecimal (0-9, A-F only)"
        return True, None

    def calculate(self, serial: str) -> str:
        """⚠️ UNVERIFIED formula — may produce wrong codes!
        
        Known Nissan serial formats:
        - BPxxxxxxxxxxxx (Blaupunkt-based)
        - CY16C-1234567 (Nissan Connect)
        - Mxxxxxxxxx (older models)
        
        For Blaupunkt BP serials: check lookup database first.
        For Nissan Connect: use official portal (free).
        """
        serial = self.format_serial(serial)
        total = sum(int(c, 16) if c.isdigit() else ord(c.upper()) - 55 for c in serial)
        code = ((total * 3) + 7777) % 10000
        return f"{code:04d}"
