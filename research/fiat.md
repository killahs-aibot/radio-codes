# Fiat Radio Code Algorithm

## Overview
- **Brand:** Fiat
- **Serial Formats:**
  - `BP` prefix (Blaupunkt)
  - `VP1` / `VP2` (500, Panda, Punto)
  - `DAIHICHI` / `MOPAR` (special variants)
  - Visteon format (Stilo, Bravo)
- **Output Code:** 4 digits
- **Works with:** 500, Panda, Punto, Stilo, Bravo, Ducato, and others

## Algorithm Type
Multiple proprietary algorithms depending on radio model and manufacturer.

## Known Implementations

### Fiat VP1 / VP2 Algorithm

For Fiat 500, 250, and similar models with VP1/VP2 head units:

Source: https://github.com/mark0wnik/VP1-VP2-Toolkit

```python
# Placeholder - actual algorithm in mark0wnik/VP1-VP2-Toolkit
# This repository contains unlock code calculator and CAN emulator
# for VP1/VP2 radios in Fiat and Alfa Romeo vehicles

def fiat_vp_vp2_code(serial):
    """
    Calculate code for Fiat VP1/VP2 radios
    """
    # Algorithm not publicly documented here
    pass
```

### Fiat Visteon (Stilo, Bravo)

From pelock.com:
- Uses serial number for lookup
- Pattern: Model-specific calculation

### Fiat Continental / MOPAR

From pelock.com Radio Code Calculator:
- Serial format: 12-character alphanumeric
- Code: 4 digits
- Algorithm proprietary

## Source Code References

### Open Source
- https://github.com/mark0wnik/VP1-VP2-Toolkit
  - Unlock code calculator AND CAN emulator for VP1/VP2
  - Works with Fiat 500, Alfa Romeo
  - Includes source code for code calculation

- https://github.com/PELock/Radio-Code-Calculator-Python
  - Paid SDK with Fiat support
  - Supports: Fiat Stilo & Bravo Visteon, Fiat DAIICHI MOPAR, Fiat 250 & 500 VP1/VP2

### Closed Source (API Required)
- https://www.pelock.com/products/fiat-250-500-vp1-vp2-radio-code-calculator-generator
- https://dev.to/bartosz/how-to-generate-radio-code-for-fiat-500-vp1vp2-1gp4

## Serial Number Locations

### On Label (Behind Radio)
Remove radio from dashboard, check sticker on top/side/bottom.

### Via Display
1. Hold preset buttons 1 and 6
2. While holding, turn radio on
3. Serial displayed on screen

### CAN Bus / OBD
Some newer Fiat vehicles store radio code in body computer.
Requires diagnostic equipment to retrieve.

## Known Test Vectors

From pelock.com documentation:
- Sample serial ending with `5849` produces valid code for Fiat 500
- Specific models require specific algorithms

## Code Entry

1. Turn ignition to ON
2. Radio shows "CODE" or enters safe mode
3. Use station preset buttons (1-4 or 5-8 depending on model)
4. Each button press advances digit (0-9, then cycles)
5. Press and hold 6th button to confirm

## Notes
- Fiat uses different radio suppliers (Blaupunkt, Visteon, Continental, DAIICHI)
- Each supplier has unique algorithm
- VP1/VP2 Toolkit is the best open source resource
- Pre-2000 Fiats often use simple 4-digit codes
- Newer systems require dealer or OBD retrieval
