# -*- coding: utf-8 -*-
"""Honda radio code — Use OFFICIAL FREE PORTAL (recommended).

STATUS: VERIFIED METHOD — Official Nissan portal is free and accurate.

Honda provides FREE radio codes at:
👉 https://radio-navicode.honda.com/

You need:
1. Vehicle VIN (from registration/documents)
2. Radio serial number (from radio screen or label)

Steps:
1. Go to https://radio-navicode.honda.com/
2. Enter your VIN
3. Enter your radio serial (press SETUP repeatedly on Honda radios)
4. Get your FREE code instantly

This is the OFFICIAL method — free, fast, and guaranteed correct.
"""
from typing import Tuple, Optional
from .base import BaseRadioAlgorithm

class HondaAlgorithm(BaseRadioAlgorithm):
    brand_name = "Honda ✅ OFFICIAL FREE PORTAL"
    supported_models = ["Civic", "Accord", "CR-V", "Jazz", "HR-V", "Fit", "e:Hev"]
    code_length = 5
    serial_pattern = r"^[A-Z0-9]{5,10}$"
    serial_format_hint = "5-10 characters (e.g. A12345)"
    serial_location = (
        "Press SETUP repeatedly until serial displays on screen.\n"
        "Or check the label on the radio casing.\n\n"
        "🌐 OFFICIAL FREE CODE: https://radio-navicode.honda.com/"
    )
    verified = True
    is_portal_only = True  # Tells UI to show portal link

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        if len(serial) < 5 or len(serial) > 10:
            return False, "Honda serial is 5-10 characters"
        return True, None

    def calculate(self, serial: str) -> str:
        """Use the OFFICIAL FREE Honda portal instead of an algorithm.

        🌐 https://radio-navicode.honda.com/

        This is free, official, and guaranteed correct.
        """
        raise NotImplementedError(
            "Honda: Use the FREE official portal instead.\n\n"
            "🌐 https://radio-navicode.honda.com/\n\n"
            "You'll need your VIN + radio serial (press SETUP on the radio).\n"
            "Free, instant, and guaranteed correct."
        )
