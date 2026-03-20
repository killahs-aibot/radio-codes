# Nissan Radio Code Algorithm

## Overview
- **Brand:** Nissan, Infiniti (Nissan group)
- **Serial Format:** 12 characters alphanumeric (e.g., CY16C-1234567)
- **Output Code:** 4-5 digits
- **Works with:** Note, Qashqai, Juke, Micra, Leaf, and other Nissan models

## Algorithm Type
**NOT publicly reversed.** Codes must be obtained via:
1. VIN-based online services (official Nissan portal)
2. EEPROM reading from radio
3. Dealer authentication

## Official Code Retrieval

### Nissan Radio-Navi Code Retrieval Portal
URL: https://radio-navicode.nissan.com

Required:
- Vehicle VIN (17 digits)
- Radio serial number

The serial number can be retrieved by:
1. Turning radio ON (shows "CODE")
2. Holding buttons 1 and 3 or 1 and 6 for ~5 seconds
3. 8-character code appears: `AYXXXXXX`
4. Or display shows `L` + last 4 digits of serial

## Serial Number Formats

| Format | Description |
|--------|-------------|
| CY16C-1234567 | 12 characters with prefix |
| B5E3-899463 | Older format |
| 12-char alphanumeric | Standard modern format |

## EEPROM Reading

For locked radios without code:

1. Remove radio from vehicle
2. Locate main processor and serial EEPROM (often 24Cxx)
3. Read EEPROM contents
4. Code stored at specific address (varies by model)
5. Calculate or extract code

## Nissan Connect / Navigation

Newer Nissan vehicles with navigation systems:
- ERC (Emergency Radio Code) system
- 16-digit serial displayed via hidden menu
- Code calculated from serial using Nissan proprietary algorithm
- Online services exist but algorithm not publicly reversed

## Source References
- https://radio-navicode.nissan.com (official portal)
- https://www.pelock.com/products/nissan-glove-box-pin-code-calculator (glove box PIN, not radio)
- https://mhhauto.com/Thread-RadioCodeDatabase-Free-for-all

## Notes
- **No public offline algorithm exists**
- Nissan uses proprietary encryption
- VIN-based lookup is the only free option (via official portal)
- EEPROM reading requires hardware and skills
- Third-party services may have proprietary algorithms
- Code format varies: 4 digits (older) to 5 digits (newer navigation)
