# Fiat VP1/VP2 Radio Code Algorithm

## Overview
- **Brand:** Fiat, Alfa Romeo
- **Serial Format:** 
  - `VP1` / `VP2` prefix + last 4 digits (e.g., VP1-1234, VP2-5678)
  - Full serial on label: many characters, only last 4 matter for code
- **Output Code:** 4 digits
- **Works with:** Fiat 500 (2007+), Fiat 250, Fiat Panda, Alfa Romeo MiTo, Alfa Romeo Giulietta

## Algorithm Type
**FULLY REVERSED** ✅ - Working open source implementation available.

## Algorithm (Python Implementation)

```python
def GetFourthByte(input):
    if input > 10:
        return 0
    return {6: 3, 7: 3, 8: 0, 9: 1}.get(input, input)

def GetThirdByte(input):
    if input > 10:
        return 0
    return {6: 2, 7: 2, 8: 0, 9: 1}.get(input, input)

def GetSecondByte(input):
    if input > 10:
        return 0
    return {6: 1, 7: 1, 8: 0, 9: 1}.get(input, input)

def GetFirstByte(input):
    if input > 10:
        return 0
    return {6: 0, 7: 0, 8: 0, 9: 1}.get(input, input)

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

## Usage

```python
# Input: Last 4 digits of serial number (as integer 0-9999)
# Output: 4-digit unlock code

code = GetCode(1234)  # Returns 4253
```

## Test Vectors

| Last 4 Digits of Serial | Code |
|-------------------------|------|
| 0000 | 1111 |
| 0001 | 1121 |
| 0123 | 3142 |
| 1234 | 4253 |
| 5000 | 1611 |
| 9999 | 2222 |

## Source Code References

### Open Source Implementation
- **Repository:** https://github.com/mark0wnik/VP1-VP2-Toolkit
- **File:** `anti-theft-code/anti-theft-code.py`
- **Language:** Python 3.9
- **License:** Not specified (open source)
- **Includes:** Unlock code calculator + CAN emulator + authorization code algorithm

### Also Includes
- **CAN Authorization Code:** Full algorithm for VP1/VP2 CAN bus authentication
- **CAN Emulator:** Arduino-based simulator for radio operation outside vehicle
- **Test Cases:** CSV files with known input/output pairs for validation

## Serial Number Location

### On Label (Behind Radio)
The serial is printed on the OEM sticker. The calculator needs only the **last 4 digits**.

### Via Display (Radio Shows Locked)
1. The radio will show "SAFE" when locked
2. Wait for code prompt
3. The serial (full) may be visible in service mode

## How the Algorithm Works

The algorithm extracts each decimal digit of the 4-digit input:
- `sn_[0]` = thousands digit
- `sn_[1]` = hundreds digit  
- `sn_[2]` = tens digit
- `sn_[3]` = units digit

Each digit is transformed through a lookup:
- Digits 0-5: returned as-is
- Digit 6: returns 0,1,2,3 for positions 0,1,2,3
- Digit 7: returns 0,1,2,3 for positions 0,1,2,3
- Digit 8: returns 0 for positions 0,1,2,3
- Digit 9: returns 1 for positions 0,1,2,3

Then combines using: `code = 1111 + third*10 + first*1000 + fourth + second*100`

## Code Entry Procedure

1. Turn ignition to ON
2. Radio shows "SAFE"
3. Wait for prompt
4. Enter 4-digit code using station preset buttons 1-4
5. Confirm with button 5 or 6 (depending on model)

## Notes

- VP1 and VP2 use the same algorithm
- Only the last 4 digits of serial are needed
- The algorithm is specifically for the "anti-theft" unlock code
- A separate CAN authorization code exists for the CAN bus handshake
- The CAN authorization algorithm is also in the repo (authcode.py)

## Recommendations for Bot Implementation

This is a **Tier 1** algorithm - fully working, free, no database needed.

Implementation:
```python
def fiat_vp_vp2_calculate(last_4_digits: str) -> str:
    """Calculate unlock code for VP1/VP2 Fiat/Alfa radios.
    
    Args:
        last_4_digits: Last 4 digits of serial number (4 numeric characters)
    Returns:
        4-digit unlock code as string
    """
    sn = int(last_4_digits)
    return f"{GetCode(sn):04d}"
```

Regex for serial validation: `^VP[12][\-]?(\d{4})$` or `^.*(\d{4})$` (accept any ending 4 digits)
