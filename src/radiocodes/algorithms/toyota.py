# -*- coding: utf-8 -*-
"""Toyota / Lexus / Scion — Use OFFICIAL DEALER or EEPROM.

STATUS: ERC SYSTEM — Dealer-only, no free algorithm.

Toyota/Lexus radios use the ERC (Emergency Radio Code) system.
The code is generated from the vehicle's master PIN stored in the M米.

Options:
1. Official dealer (may charge)
2. Independent garage with Toyota SDP (subs cost ~£10-20)
3. EEPROM reading — guaranteed, no dealer needed

For EEPROM reading: Use CH341A programmer + full chip scan.
The Toyota radio code is typically stored at known addresses in the EEPROM.
"""
from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

class ToyotaAlgorithm(BaseRadioAlgorithm):
    brand_name = "Toyota / Lexus ⚠️ DEALER or EEPROM"
    supported_models = ["Aygo", "Yaris", "Corolla", "C-HR", "Rav4", "Prius", "Lexus IS/ES/NX/RX"]
    code_length = 4
    serial_pattern = r"^[A-Z0-9]{6,12}$"
    serial_format_hint = "6-12 characters on radio label"
    serial_location = "Remove radio, check label. Or check vehicle documents."
    verified = False  # No free algorithm exists

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        return True, None

    def calculate(self, serial: str) -> str:
        """No free algorithm exists for Toyota/Lexus.

        Options:
        1. Dealer — may charge ~£10-20
        2. Independent garage with Toyota SDP — ~£10
        3. EEPROM reading — guaranteed, DIY

        For EEPROM: Use CH341A programmer, full chip scan finds the code.
        """
        raise NotImplementedError(
            "Toyota/Lexus: No free algorithm available (ERC system).\n\n"
            "Options:\n"
            "1. 🌐 Dealer — may charge ~£10-20\n"
            "2. 🔧 Independent garage with Toyota SDP\n"
            "3. 💾 EEPROM reading (CH341A + full chip scan)\n\n"
            "The EEPROM method is DIY and guaranteed correct."
        )
