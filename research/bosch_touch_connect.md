# BOSCH Touch & Connect Radio Code Algorithm

## Overview
- **Brand:** Opel / Vauxhall (BOSCH manufactured)
- **Serial Format:** 
  - `CM0xxx` prefix (e.g., CM0123...xxx)
  - Device number: `7612830xxx`
- **Output Code:** 4 digits (presumed)
- **Works with:** Opel/Vauxhall vehicles with BOSCH Touch & Connect infotainment

## Algorithm Type
**NOT REVERSED** - No public algorithm exists for this radio.

## Serial Number Formats

### Format 1: CM0xxx Serial
```
CM0XXXXXXXX (10+ characters, starts with CM0)
```
- Found on BOSCH Touch & Connect units
- 10-character minimum observed

### Format 2: Device Number
```
7612830XXXXXXXX (13 digits, starts with 7612830)
```
- Alternative identifier found on label
- 7612830 prefix is consistent across BOSCH units

## Known Information

From research, the BOSCH Touch & Connect radio is used in:
- Opel Insignia (2008-2017)
- Opel Astra (2009-2015)
- Opel Zafira (2008-2019)

### Multiple Input Requirement
Sources mention that BOSCH Touch & Connect requires **3 inputs** to calculate the code:
1. Serial number (CM0xxx format)
2. Device number (7612830xxx format)
3. Unknown 3rd input

The third input is not yet identified. Candidates could be:
- VIN number
- Another serial/lock code from display
- Radio model number

## Code Retrieval Methods

### Method 1: EEPROM Reading
The radio code can be extracted by:
1. Removing radio from vehicle
2. Reading the serial EEPROM (often 24Cxx family)
3. Locating the 4-digit code at a known memory address

### Method 2: Diagnostic Equipment
- OpelCOM / Vauxhall diagnostic software
- Generic OBD diagnostic tools (some models)
- Dealer-level equipment (most reliable)

### Method 3: Online Services
- code-radio.com (paid)
- onlineradiocodes.co.uk (paid)

## Source References
- https://www.code-radio.com/radio-code/opel
- https://mhhauto.com/Thread-RadioCodeDatabase-Free-for-all
- https://www.carstereocode.com/unlock.php?mk=28

## Research Status
- ❌ **NO algorithm found**
- ❓ 3 inputs mentioned but 3rd input unidentified
- 🔍 EEPROM reading is the most viable offline method
- 📊 Could potentially build database from forum posts

## Forum Posts with Serial+Code Pairs Needed
Search for:
- `"BOSCH Touch & Connect"` + `"CM0"` + code on:
  - mhhauto.com
  - unlockforum.com
  - vauxhallforum.co.uk
  - paddle.com (Opel owners forum)

## Next Steps for Research
1. Find forum posts with CM0xxx serials and their codes
2. Identify what the 3rd required input is
3. Check if the EEPROM address is consistent across units
4. Look for BOSCH service manuals
