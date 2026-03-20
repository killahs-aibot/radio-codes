# Honda Radio Code Algorithm

## Overview
- **Brand:** Honda, Acura (Honda group)
- **Serial Format:** 8 digits displayed (format: XXXXXXXX)
- **Output Code:** 5 digits
- **Works with:** Civic, Accord, CR-V, Jazz, Fit, and other Honda models

## Algorithm Type
**NOT publicly reversed.** The serial number is used for lookup via:
1. Official Honda website (radio-navicode.honda.com)
2. Dealer systems
3. Third-party databases (proprietary)

## How to Get Code (Official Method)

### Online Retrieval
1. Visit: https://radio-navicode.honda.com
2. Enter:
   - Vehicle VIN (17 digits)
   - ZIP code
   - Radio serial number
3. Receive code via email or screen display

### Via Radio Display
For radios with "COdE" display:
1. Turn ignition to ON
2. Turn radio ON (shows COdE)
3. Press and hold the top of the SEEK/AM/FM button
4. While holding, press and release the MPWR button
5. Serial number appears: `UXXXXXXX` or `L####`
6. Write down serial, then continue holding to cycle through

### Sticker in Glovebox
Some Honda vehicles have the radio code on a sticker inside the glovebox.
Check the white sticker with barcode.

## Serial Number Display Pattern

From Honda documentation:
```
L0055  (L + last 4 digits)
U12345678 (U + 8 digits)
```

Ignore the U or L prefix - write down all 8 digits.

## Code Format
- **5 digits** (e.g., 12345, 00000)
- Some older units use 4 digits

## EEPROM Reading

For locked radios without code:
1. Remove radio from vehicle
2. Locate EEPROM chip on main board
3. Read contents via EEPROM reader
4. Code stored at specific memory address
5. Some Honda radios use simple XOR or addition algorithm

## Source References
- https://radio-navicode.honda.com (official US portal)
- https://radio-navicode.acura.com (official Acura portal)
- https://mygarage.honda.com/s/serial-number-help

## Honda/Acura Serial Retrieval

### Standard Procedure
1. With radio OFF, press and hold the 1 and 6 buttons
2. While holding, press the power button
3. Watch display for serial number
4. Release buttons

### Navigation System
1. Press and hold the hard disk button
2. While holding, press the display screen corners
3. Enter hidden menu for system information

## Notes
- **No public algorithm exists**
- Honda uses VIN + serial for verification
- Official portal requires vehicle registration or VIN
- Third-party services may use proprietary algorithms
- Acura uses same system as Honda
- 5-digit codes are standard for 2003+ vehicles
