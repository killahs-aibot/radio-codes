# Blaupunkt CAR 2003 / CAR 2004 Radio Code

## Overview
- **Brand:** Vauxhall / Opel (Blaupunkt manufactured)
- **Serial Format:** 
  - `GM0203xxxxxxx` prefix (e.g., GM0203AB123456)
  - 14-character total, alphanumeric
- **Output Code:** 4 digits
- **Works with:** Vauxhall/Opel vehicles with Blaupunkt CAR 2003 / CAR 2004 radios

## Algorithm Type
**NOT FULLY REVERSED** - Forum evidence suggests an algorithm exists, but it has not been publicly documented.

## Serial Number Format

### GM0203 Format (Confirmed)
```
GM0203XXXXXXXX (14 characters total)
```
- Starts with `GM0203`
- Followed by alphanumeric characters
- Found on Blaupunkt CAR 2003 units

### Alternative Serial Formats on Same Unit
Some units also show shorter serials:
- `7XXXXXXXXX` (10 digits, starts with 7)
- `GM` + 12 alphanumeric

## Evidence an Algorithm Exists

From forum research:
- Multiple posts on mhhauto.com and unlockforum.com mention entering serial and receiving code
- Some sources claim the CAR 2003 uses the same algorithm as CD30/MP3
- CRUCC software (carstereocode.com) supports this model

## Forum Sources with Serial+Code Pairs

### Key Forum URLs to Search:
1. https://mhhauto.com/Thread-RadioCodeDatabase-Free-for-all
2. https://unlockforum.com/forumdisplay.php?70-Car-Radio-Unlock
3. https://www.elektroda.com/rtvforum/f118.htm

### Forum Search Queries:
- `"GM0203"` + code
- `"CAR 2003"` + unlock code
- `"Blaupunkt CAR 2003"` + serial

## Source References
- https://www.carstereocode.com/unlock.php?mk=28
- https://mhhauto.com/Thread-RadioCodeDatabase-Free-for-all
- https://www.code-radio.com/radio-code/opel

## Research Status
- ⚠️ **Algorithm suspected but NOT confirmed**
- 🔍 Forum posts may contain enough data to reverse engineer
- 📊 Could use CRUCC software to generate test vectors
- 💾 EEPROM reading viable as fallback

## Recommendations
1. Scrape MHH AUTO RadioCodeDatabase thread for GM0203 entries
2. Cross-reference with CAR 2003 owners on vauxhall forums
3. Consider purchasing CRUCC to test against known serials
