# -*- coding: utf-8 -*-
"""
Fiat / Alfa Romeo VP1 / VP2 Radio Code Algorithm.

CONFIRMED ALGORITHM — from github.com/mark0wnik/VP1-VP2-Toolkit
Test vectors verified: 0000→1111, 0123→3142, 1234→4253, 5000→1611, 9999→2222

Works with:
- Fiat 500 (2007+)
- Fiat 250 (Panda)
- Alfa Romeo MiTo
- Alfa Romeo Giulietta
- VP1 and VP2 head units

Usage: Take the LAST 4 DIGITS of the serial number (or full serial, last 4 chars),
pass as integer to GetCode().

Serial format examples:
- VP1-1234 → use 1234
- VP2-5678 → use 5678
- FULL:SN:VP1:A123456 → use 3456
"""

from typing import Tuple, Optional
from .base import BaseRadioAlgorithm


def _GetFourthByte(input_val: int) -> int:
    if input_val > 10:
        return 0
    return {6: 3, 7: 3, 8: 0, 9: 1}.get(input_val, input_val)


def _GetThirdByte(input_val: int) -> int:
    if input_val > 10:
        return 0
    return {6: 2, 7: 2, 8: 0, 9: 1}.get(input_val, input_val)


def _GetSecondByte(input_val: int) -> int:
    if input_val > 10:
        return 0
    return {6: 1, 7: 1, 8: 0, 9: 1}.get(input_val, input_val)


def _GetFirstByte(input_val: int) -> int:
    if input_val > 10:
        return 0
    return {6: 0, 7: 0, 8: 0, 9: 1}.get(input_val, input_val)


def GetCode(sn: int) -> int:
    """
    Calculate 4-digit radio code from last 4 digits of serial.
    
    Args:
        sn: Last 4 digits of serial as integer (0-9999)
    Returns:
        4-digit unlock code
    """
    code = 1111
    sn_ = [
        ((sn // 1000) & 0x0F),       # thousands digit
        ((sn % 1000) // 100 & 0x0F), # hundreds digit
        ((sn % 100) // 10 & 0x0F),   # tens digit
        ((sn % 10) & 0x0F),          # units digit
    ]
    code += (_GetThirdByte(sn_[3]) * 10)
    code += (_GetFirstByte(sn_[2]) * 1000)
    code += (_GetFourthByte(sn_[1]))
    code += (_GetSecondByte(sn_[0]) * 100)
    return code


class FiatAlgorithm(BaseRadioAlgorithm):
    brand_name = "Fiat / Alfa Romeo"
    supported_models = [
        "VP1 (Fiat 500, Alfa MiTo)",
        "VP2 (Fiat 250, Alfa Giulietta)",
        "Fiat 500 (2007+)",
        "Fiat Panda (2012+)",
        "Alfa Romeo MiTo",
        "Alfa Romeo Giulietta",
    ]
    code_length = 4
    serial_pattern = r"^VP[12][\-]?(\d{4})$"
    serial_format_hint = "Last 4 digits of serial (e.g. VP1-1234 → enter 1234)"
    serial_location = (
        "OPTION 1 — On the radio label (behind the unit):\n"
        "  Remove radio from dashboard\n"
        "  Look for serial starting with VP1 or VP2\n"
        "  Use the LAST 4 DIGITS only\n\n"
        "OPTION 2 — From locked radio display:\n"
        "  Radio shows 'SAFE' when locked\n"
        "  Enter wrong code 3 times\n"
        "  Serial may appear on display\n\n"
        "OPTION 3 — CAN bus:\n"
        "  Radio communicates VP1/VP2 codes via CAN\n"
        "  Use VP1-VP2-Toolkit CAN emulator to read"
    )

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        # Accept last 4 digits (numeric) or VP1/VP2 format
        serial = serial.upper().replace(" ", "").replace("-", "")
        
        # Extract last 4 digits
        if len(serial) >= 4:
            last4 = serial[-4:]
            if last4.isdigit():
                return True, None
        
        # Try raw 4-digit
        if serial.isdigit() and len(serial) == 4:
            return True, None
        
        return False, "Enter the last 4 digits of your serial (e.g. 1234)"

    def calculate(self, serial: str) -> str:
        serial = serial.upper().replace(" ", "").replace("-", "")
        
        # Extract last 4 digits
        last4 = serial[-4:]
        if not last4.isdigit():
            raise ValueError(f"Could not extract last 4 digits from {serial}")
        
        sn = int(last4)
        code = GetCode(sn)
        return f"{code:04d}"
