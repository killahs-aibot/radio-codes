# -*- coding: utf-8 -*-
"""⚠️  UNVERIFIED — Peugeot / Citroën radio code algorithm.

STATUS: UNVERIFIED — This formula has NOT been publicly confirmed.
        It may produce WRONG codes. USE WITH CAUTION.

Peugeot/Citroën serial formats:
- BPxxxxxxxxxxxx (Blaupunkt)
- 815xxxxxxxxxxx (Valeo)
- 7xxxxxxxxxxx (Siemens)

For guaranteed correct codes: EEPROM reading recommended.
Known working approach: Full chip scan mode in EEPROM Reader.
"""
from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

class PeugeotAlgorithm(BaseRadioAlgorithm):
    brand_name = "Peugeot / Citroën ⚠️ UNVERIFIED"
    supported_models = ["RT3", "RT4", "RNEG", "MyWay", "WipNav", "WipCom"]
    code_length = 4
    serial_pattern = r"^[A-Z0-9]{4,20}$"
    serial_format_hint = "4-20 characters on radio label"
    serial_location = (
        "RT3/RT4: Press SETUP repeatedly until serial displayed.\n"
        "Or remove radio and check label on casing."
    )
    verified = False  # 🔴 NOT VERIFIED

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        if len(serial) < 4:
            return False, "Serial too short"
        return True, None

    def calculate(self, serial: str) -> str:
        """⚠️ UNVERIFIED formula — may produce wrong codes!
        
        Known Peugeot/Citroën pairs from forum data:
        - BP2774S7838642 → 7139 (Peugeot 407)
        - BP8146Y5935543 → 2040
        
        For Blaupunkt BP serials: check the lookup database first.
        """
        serial = self.format_serial(serial)
        total = 0
        for i, c in enumerate(serial):
            if c.isdigit():
                val = int(c)
            else:
                val = ord(c.upper()) - ord('A') + 10
            total += val << (i * 2)
        code = ((total ^ 0x1357) + 5000) % 10000
        return f"{code:04d}"
