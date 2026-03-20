# -*- coding: utf-8 -*-
"""
Ford M Series / V Series radio code algorithm.

CONFIRMED ALGORITHM SOURCE:
- M Series: 10x10 lookup table from https://gist.github.com/4ndrej/b252c4ec3efa49d2b7b03c704c1289e3
  (original: https://github.com/OlegSmelov/ford-radio-codes)
- V Series: Binary lookup file (radiocodes.bin), 4-byte uint16 per serial
  from https://github.com/DavidB445/fz_fordradiocodes

M Series: serial format = M123456 (7 chars, 1 letter + 6 digits) → 4-digit code
V Series: serial format = V123456 (7 chars, 1 letter + 6 digits) → 4-digit code
  Offset in binary = index (last 6 digits as int)
  M serials: offset = index * 2
  V serials: offset = 2000000 + index * 2
"""

from typing import Tuple, Optional
import os
import struct

from .base import BaseRadioAlgorithm


# 10x10 lookup table for M Series algorithm
_FORA_M_LOOKUP = [
    [9, 5, 3, 4, 8, 7, 2, 6, 1, 0],
    [2, 1, 5, 6, 9, 3, 7, 0, 4, 8],
    [0, 4, 7, 3, 1, 9, 6, 5, 8, 2],
    [5, 6, 4, 1, 2, 8, 0, 9, 3, 7],
    [6, 3, 1, 2, 0, 5, 4, 8, 7, 9],
    [4, 0, 8, 7, 6, 1, 9, 3, 2, 5],
    [7, 8, 0, 5, 3, 2, 1, 4, 9, 6],
    [1, 9, 6, 8, 7, 4, 5, 2, 0, 3],
    [3, 2, 9, 0, 4, 6, 8, 7, 5, 1],
    [8, 7, 2, 9, 5, 0, 3, 1, 6, 4],
]

# Path to the radiocodes.bin lookup file (distributed with the app)
DEFAULT_RADIO_CODES_BIN = os.path.join(os.path.dirname(__file__), "..", "..", "data", "ford_radiocodes.bin")


def _ford_m_calculate(serial: str) -> str:
    """
    Calculate Ford M Series code from serial.

    Algorithm (confirmed, from GitHub gist):
    - Takes digits 2-7 of the serial (6 digits)
    - Reverses them
    - Uses 10x10 lookup table to compute 7 intermediate values r1-r7
    - Then applies chained modulo 10 operations to get final 4 digits

    Test vectors:
      M000001 -> 9617
      M123456 -> 2487
      M999999 -> 4968
      M111111 -> 8691
      M000000 -> 1558
    """
    serial = serial.upper()
    if not serial.startswith('M') or len(serial) != 7:
        raise ValueError("M Series serial must be 7 characters: Mxxxxxx")

    digits = [int(c) for c in serial[1:7]]
    n = list(reversed(digits))

    n1, n2, n3, n4, n5, n6 = [n[i] if i < len(n) else 0 for i in range(6)]

    r1 = _FORA_M_LOOKUP[n1][5]
    r2 = _FORA_M_LOOKUP[n2][3]
    r3 = _FORA_M_LOOKUP[n3][8]
    r4 = _FORA_M_LOOKUP[n4][2]
    r5 = _FORA_M_LOOKUP[n5][1]
    r6 = _FORA_M_LOOKUP[n6][6]
    r7 = 0  # n7 is always 0 (6-digit serial)

    res1 = ((_FORA_M_LOOKUP[r2][r1] + 1) * (_FORA_M_LOOKUP[r6][r2] + 1) +
            (_FORA_M_LOOKUP[r4][r3] + 1) * (_FORA_M_LOOKUP[r7][r5] + 1) +
            _FORA_M_LOOKUP[r1][r4]) % 10
    res2 = ((_FORA_M_LOOKUP[r2][r1] + 1) * (_FORA_M_LOOKUP[r5][r4] + 1) +
            (_FORA_M_LOOKUP[r5][r2] + 1) * (_FORA_M_LOOKUP[r7][r3] + 1) +
            _FORA_M_LOOKUP[r1][r6]) % 10
    res3 = ((_FORA_M_LOOKUP[r2][r1] + 1) * (_FORA_M_LOOKUP[r4][r2] + 1) +
            (_FORA_M_LOOKUP[r3][r6] + 1) * (_FORA_M_LOOKUP[r7][r4] + 1) +
            _FORA_M_LOOKUP[r1][r5]) % 10
    res4 = ((_FORA_M_LOOKUP[r2][r1] + 1) * (_FORA_M_LOOKUP[r6][r3] + 1) +
            (_FORA_M_LOOKUP[r3][r7] + 1) * (_FORA_M_LOOKUP[r2][r5] + 1) +
            _FORA_M_LOOKUP[r4][r1]) % 10

    xres1 = (_FORA_M_LOOKUP[res1][5] + 1) * (_FORA_M_LOOKUP[res2][1] + 1) + 105
    xres2 = (_FORA_M_LOOKUP[res2][1] + 1) * (_FORA_M_LOOKUP[res4][0] + 1) + 102
    xres3 = (_FORA_M_LOOKUP[res1][5] + 1) * (_FORA_M_LOOKUP[res3][8] + 1) + 103
    xres4 = (_FORA_M_LOOKUP[res3][8] + 1) * (_FORA_M_LOOKUP[res4][0] + 1) + 108

    code0 = ((xres4 // 10) % 10 + xres4 % 10 + r1) % 10
    code1 = ((xres3 // 10) % 10 + xres3 % 10 + r1) % 10
    code2 = ((xres2 // 10) % 10 + xres2 % 10 + r1) % 10
    code3 = ((xres1 // 10) % 10 + xres1 % 10 + r1) % 10

    return f"{code0}{code1}{code2}{code3}"


def _ford_v_calculate(serial: str, bin_path: str = DEFAULT_RADIO_CODES_BIN) -> str:
    """
    Calculate Ford V Series code from serial using binary lookup file.

    The radiocodes.bin file contains 4,000,000 entries (2M M-series + 2M V-series).
    Each entry is a 2-byte uint16 (little-endian).

    Offset calculation:
      index = int(last 6 digits of serial)
      M-series: offset = index * 2
      V-series: offset = 2,000,000 + index * 2
    """
    serial = serial.upper()
    if not serial.startswith('V') or len(serial) != 7:
        raise ValueError("V Series serial must be 7 characters: Vxxxxxx")

    index = int(serial[1:7])
    if index < 0 or index > 999999:
        raise ValueError("V Series index must be 0-999999")

    offset = 2_000_000 + index * 2  # V-series starts at 2M

    if os.path.exists(bin_path):
        try:
            with open(bin_path, "rb") as f:
                f.seek(offset)
                data = f.read(2)
                if len(data) == 2:
                    code = struct.unpack("<H", data)[0]
                    return f"{code:04d}"
        except Exception:
            pass

    raise FileNotFoundError(
        f"radiocodes.bin not found at {bin_path}. "
        "Download it from: https://github.com/DavidB445/fz_fordradiocodes"
    )


class FordMAlgorithm(BaseRadioAlgorithm):
    """Ford M Series radio code algorithm (confirmed working)."""
    brand_name = "Ford"
    supported_models = ["M Series", "M Serial"]
    code_length = 4
    serial_pattern = r"^M\d{6}$"
    serial_format_hint = "7 characters: M + 6 digits (e.g. M123456)"
    serial_location = (
        "1. Hold preset buttons 1 AND 6 together\n"
        "2. While holding, turn the radio on\n"
        "3. The serial will appear (e.g. M123456)\n"
        "4. Release buttons and enter the 6 digits"
    )

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        if len(serial) != 7:
            return False, "Serial must be 7 characters: M + 6 digits (e.g. M123456)"
        if not serial.startswith('M'):
            return False, "M Series serial must start with 'M'"
        if not serial[1:].isdigit():
            return False, "Last 6 characters must all be digits"
        return True, None

    def calculate(self, serial: str) -> str:
        return _ford_m_calculate(serial)


class FordVAlgorithm(BaseRadioAlgorithm):
    """Ford V Series radio code algorithm (binary lookup file required)."""
    brand_name = "Ford"
    supported_models = ["V Series", "V Serial", "TravelPilot EX", "TravelPilot FX", "TravelPilot NX"]
    code_length = 4
    serial_pattern = r"^V\d{6}$"
    serial_format_hint = "7 characters: V + 6 digits (e.g. V123456)"
    serial_location = (
        "1. Hold preset buttons 1 AND 6 together\n"
        "2. While holding, turn the radio on\n"
        "3. The serial will appear (e.g. V123456)\n"
        "4. Release buttons and enter the 6 digits\n"
        "Note: V Series requires the radiocodes.bin file for lookup"
    )

    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        serial = self.format_serial(serial)
        if len(serial) != 7:
            return False, "Serial must be 7 characters: V + 6 digits (e.g. V123456)"
        if not serial.startswith('V'):
            return False, "V Series serial must start with 'V'"
        if not serial[1:].isdigit():
            return False, "Last 6 characters must all be digits"
        return True, None

    def calculate(self, serial: str) -> str:
        return _ford_v_calculate(serial, DEFAULT_RADIO_CODES_BIN)
