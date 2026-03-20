# Volkswagen RCD Radio Code Algorithm

## Overview
- **Brand:** Volkswagen
- **Serial Formats:** 
  - `VWZ` + 11 characters (most common - RCD 210/310/510, RNS 310/510)
  - `AUZ` + characters (some Audi/VW models)
  - Other older formats (Gamma, Beta, Alpha)
- **Output Code:** 4 digits (typically 0000-1999 range observed)
- **Works with:** Golf, Polo, Passat, Tiguan, and other VW models 1998-2016

## Algorithm Type
The VW algorithm has NOT been publicly reversed. Codes are obtained via:
1. Pre-computed databases from forum posts
2. Online paid services
3. EEPROM reading (for some models)

## Known Serial-to-Code Mappings

From VW Vortex forum thread (https://gist.github.com/VWZ1Z2Y5298166/e44d7c51f54d8b6094c39cd11ad62062):

| VIN | Serial | Code |
|-----|--------|------|
| 3VWSA81H9WM112789 | VWZ9Z7V3888887 | 0006 |
| WVWZZZ1KZ9W091014 | VWZ627J9030185 | 0027 |
| 3VWSE69M03M159960 | VWZ5Z7B5013069 | 0031 |
| 3VWRF71K66M722316 | VWZ4Z7H2200493 | 0037 |
| 3VWSE29M6YM145996 | VWZ9Z7Y7189266 | 0042 |
| 9BWDE61J324008978 | VWZ4Z7A4108703 | 0053 |
| WVWBA71K78W169424 | VWZ2Z2D1171510 | 0062 |
| 3VWRC81H7RM067459 | VWZ5Z7P0675631 | 0063 |
| 9BWDE61J234027071 | VWZ5Z7B5125847 | 0081 |
| 3VWRA81H1VM063309 | VWZ2Z2D1524411 | 0104 |
| WVWZZZ1KZ6W169238 | VWZ2Z2D2185011 | 0215 |
| WVWWH63B13E009509 | VWZ5Z7A5026282 | 0233 |
| 3VWBC81H2SM047112 | VWZ9Z7S2988343 | 0274 |
| 3VWRF81H6WM128934 | VWZ9Z7S3182223 | 0323 |
| WVGZZZ1TZ8W012498 | VWZ1Z2G7236438 | 0343 |
| 1VWFA0172GV010560 | VWZ9Z7B0033961 | 0359 |
| 3VWPA81H1XM238619 | VWZ4Z7X5007973 | 0400 |
| 3VWNN01H4RM058874 | VWZ5Z7P0661913 | 0405 |
| 3VWVH69M03M121309 | VWZ5Z7A1012819 | 0422 |
| WVWZZZ9CZ1M603415 | VWZ1Z3Y6183262 | 0516 |
| 3VWHD81H7TM045008 | VWZ9Z7V3755232 | 0855 |
| WVWBA21J1YW221222 | VWZ2Z2E2704379 | 0867 |
| WVWNL73C19E540226 | VWZ5Z7H2279696 | 0887 |
| WVWVD63BX2E264634 | VWZ5Z7A1033520 | 0923 |
| WVWBA71K78W169424 | VWZ1Z7E5091017 | 0825 |
| 3VWSE69M43M096751 | VWZ927B0068567 | 1889 |
| 9BWKE61J334067148 | VWZ5Z7C5232416 | 1907 |

## Observed Patterns

Analysis of the VWZ serial data suggests:
- **Serial prefix:** VWZ9Z7X, VWZ5Z7X, VWZ4Z7X, VWZ2Z2X, VWZ1Z2X, etc.
- **Code range:** 0000-1999 observed (not all 0000-9999)
- **No obvious algorithmic pattern** visible from serial to code
- Likely a proprietary algorithm or table lookup

## VWZ Serial Structure
```
VWZ [1-2 digits] [Z or number] [2 digits] [letter] [7 digits]
```

Example: `VWZ5Z7B5013069`
- VWZ5Z - Type/lock digits
- 7B - Model identifier  
- 5013069 - Unit serial

## How to Get Code (Without Algorithm)

### Method 1: Forum Database Lookup
Search VW Vortex and other forums for your serial number.

### Method 2: EEPROM Reading
For locked radios, the code can be extracted by:
1. Removing radio from vehicle
2. Reading the serial EEPROM (often 24Cxx family)
3. Locating the 4-digit code at a known address

### Method 3: Online Services
- pelock.com (paid API)
- Various other paid services

## Source References
- https://gist.github.com/VWZ1Z2Y5298166/e44d7c51f54d8b6094c39cd11ad62062
- https://unlockradiocode.com/brands/volkswagen-radio-code
- https://radiocodeford.com/vw-radio-code

## Notes
- VW algorithm has NOT been publicly reversed
- The 4-digit code is embedded in radio EEPROM, not computed from serial
- Some newer models use different security mechanisms
- If SAFE is displayed, leave radio powered on 60-90 minutes before entering code
