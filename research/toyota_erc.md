# Toyota ERC (Emergency Radio Code) Algorithm

## Overview
- **Brand:** Toyota, Lexus (Toyota group)
- **Serial Format:** 16 digits (ERC serial number)
- **Output Code:** 4-6 digits (varies by model)
- **Works with:** Japanese-market Toyota navigation and audio systems

## Algorithm Type
**NOT publicly reversed.** The ERC (Emergency Radio Code) system uses:
1. 16-digit serial number (ERC serial)
2. Model number
3. Proprietary Toyota algorithm

## How to Get ERC Serial

### Hidden Menu Method
1. Press and hold buttons 1, 3, 6, and Track Up simultaneously
2. While holding, turn parking lights on/off 3-4 times
3. A new screen appears with serial numbers
4. Write down the 16-character ERC serial number

### Label on Radio/Navigation Unit
Remove the unit and check the label for:
- Model number
- Serial number (16 digits)
- Part number

### Vehicle Documents
Some Toyota vehicles have the ERC code recorded in:
- Owner's manual
- Service history file
- Glovebox documentation

## Serial Number Format

```
16 alphanumeric characters
Example: 14ABC1234567890
```

The serial encodes:
- First 2 characters: Region/model identifier
- Remaining 14 characters: Unit-specific serial

## Code Retrieval Methods

### Official Toyota Resources
1. **Dealer:** Provide VIN and ownership proof
2. **Owner's Portal:** Some regions offer online retrieval
3. **Service Manual:** Code sometimes printed in manual

### Third-Party Services
- pelock.com ERC Calculator (paid)
- Various app-based calculators
- These services have proprietary (not public) algorithms

## Source References
- https://www.erccalculator.com/en (ERC Calculator)
- https://www.pelock.com/products/toyota-erc-calculator-radio-unlock-code-generator
- https://jpchecker.com/blogs/view/toyota-navigation-unlock-free-erc-code-decoder-complete-guide-2026

## Code Format by Model

| Model/Year | Code Length |
|------------|-------------|
| Pre-2000 | 4 digits |
| 2000-2010 | 4-5 digits |
| 2010+ Navigation | 5-6 digits |

## EEPROM Extraction

For locked units without code:
1. Remove navigation/audio unit
2. Locate flash memory or EEPROM
3. Read memory contents
4. Find code at known offset (varies by hardware generation)
5. Some units store code in plain text

## Notes
- **No publicly reversed algorithm exists**
- ERC system is Toyota's proprietary anti-theft
- Algorithm varies by head unit manufacturer (Panasonic, Pioneer, Denso)
- Japanese-market units have different system than US/European
- Third-party calculators use undisclosed algorithms
- Some newer Toyota use "Security" button + smartphone app
