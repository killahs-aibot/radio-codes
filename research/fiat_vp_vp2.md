# Fiat VP1/VP2 Radio Unlock Algorithm Research

## Source
Repository: https://github.com/mark0wnik/VP1-VP2-Toolkit
Author: mark0wnik
License: MIT

## Overview
This toolkit provides three main components for VP1/VP2 radios found in Fiat and Alfa Romeo vehicles:
1. Anti-Theft Code Calculator
2. Authorization Code Algorithm (CAN-based)
3. Car CAN Emulator (Arduino-based)

## 1. Anti-Theft Code Calculator (`anti-theft-code/`)

### Files
- `anti-theft-code.py` - Main Python script for calculating unlock codes
- `README.MD` - Instructions
- `location.jpg` - Photo showing serial number location

### Algorithm
The algorithm takes the **last 4 digits of the radio serial number** and produces a 4-digit code.

```python
def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False

def GetFourthByte(input):
    if (input > 10):
        return 0
    return {
        6: 3,
        7: 3,
        8: 0,
        9: 1
    }.get(input, input)

def GetThirdByte(input):
    if (input > 10):
        return 0
    return {
        6: 2,
        7: 2,
        8: 0,
        9: 1
    }.get(input, input)

def GetSecondByte(input):
    if (input > 10):
        return 0
    return {
        6: 1,
        7: 1,
        8: 0,
        9: 1
    }.get(input, input)

def GetFirstByte(input):
    if (input > 10):
        return 0
    return {
        6: 0,
        7: 0,
        8: 0,
        9: 1
    }.get(input, input)

def GetCode(sn):
    code = 1111
    sn_ = [((sn // 1000) & 0x0F),
           ((sn % 1000) // 100 & 0x0F),
           ((sn % 100) // 10 & 0x0F),
           ((sn % 10) & 0x0F)]
    code += (GetThirdByte(sn_[3]) * 10)
    code += (GetFirstByte(sn_[2]) * 1000)
    code += (GetFourthByte(sn_[1]))
    code += (GetSecondByte(sn_[0]) * 100)
    return code
```

### How It Works
1. Takes last 4 digits of serial number (as integer)
2. Splits into 4 nibbles (4-bit chunks)
3. Each nibble maps to a position in the output code using lookup tables
4. Starting value is 1111, then adds positional contributions
5. Returns 4-digit code

### Usage
```bash
python anti-theft-code.py 1234
python anti-theft-code.py 5678 9012 3456  # multiple at once
```

## 2. CAN Authorization Code (`can-authorization-code/`)

### Files
- `authcode.py` - Main algorithm implementation with BitArray manipulation
- `auth-code-can-responder.py` - Arduino CAN responder script
- `01_0000-FFFF_00_0000.csv` - Test vectors for initialization (645KB, ~65K rows)
- `01_C170_00_0000-FFFF.csv` - Test vectors for code calculation (648KB)
- `README.MD` - Algorithm documentation

### Algorithm
The CAN authorization code uses a complex bit manipulation function operating on 16-bit values:

```python
from bitstring import BitArray

def code(value: BitArray, init=0x00, config: BitArray=BitArray(hex='0000')):
    res = BitArray(hex='0000')
    # 16 output bits, each computed from input bits with XOR/XNOR patterns
    # Specific bits checked: 0xb, 0xc, 0xd, 0xe, 0xf, 0x9, 0x8, 0x7, 0x6, 0x5, 0x4, 0x3, 0x2, 0x1, 0x0
    # Special case: value.uint == 0x60f triggers additional inversions
    return res
```

### Two-Stage Process
1. **Initialization**: Compute config from a known input (typically 0xC170) with init=0x01
2. **Code Generation**: Compute output from challenge value with init=0x00 and the config

### Key Constants
- Init vector: `0xC170` (used in test file name)
- Special case value: `0x60f` (triggers extra XOR inversions across multiple bits)

## 3. CAN Emulator (`can-emulation/`)

Arduino-based hardware project that simulates car CAN bus to allow radio operation outside the vehicle.

## Radio Models Covered
- Fiat VP1 / VP2 stereos
- Alfa Romeo compatible units
- Bosch Touch & Connect (related systems)

## Serial Number Format
Typically found on a sticker on the radio casing. Format varies by model.

## References
- OSCR (Opel Security Code Reader) - related tool for reading EEPROM dumps
- CH341A programmer - hardware for reading 24/25/95 series EEPROM chips
- https://mbrdar.gitlab.io/radio-unlock/opel - free online decoder for Opel EEPROM dumps
