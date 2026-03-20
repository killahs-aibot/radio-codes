# Opel / Vauxhall Radio Code Algorithm

## Overview
- **Brand:** Opel (Europe), Vauxhall (UK)
- **Serial Format:** 
  - `GM` + 12 digits/letters (most common)
  - Part number starting with 7 + 10 digits
- **Output Code:** 4 digits
- **Works with:** Astra, Corsa, Zafira, Insignia, and other Opel/Vauxhall models

## Algorithm Type
Pre-computed lookup table/database approach. The exact algorithm has not been 
publicly documented, but the serial format and lookup process are well-understood.

## Serial Number Formats

### Format 1: GM Serial (Most Common)
```
GMXXXXXXXXXXXX (14 characters total)
```
- Starts with letters GM
- Contains 12 alphanumeric characters
- Found on newer models (CD30, CD70, DVD90, etc.)

### Format 2: Part Number
```
7XXXXXXXXXX (10 digits, starts with 7)
```
- Older model format
- Located on radio label

## Code Retrieval Methods

### Method 1: Serial Lookup (Online)
Enter serial number at:
- https://www.code-radio.com/radio-code/opel
- https://www.onlineradiocodes.co.uk/vauxhall-radio-codes

### Method 2: VIN-Based (Some Models)
For newer vehicles with CAN bus integration, the code can be retrieved via:
- Dealer diagnostic equipment
- Aftermarket diagnostic tools (OpelCOM, etc.)

### Method 3: EEPROM Reading
The radio contains an EEPROM (often 24Cxx) that stores the security code.
Reading the EEPROM at a known address can reveal the code directly.

## Known Information

From MHH AUTO RadioCodeDatabase (https://mhhauto.com/Thread-RadioCodeDatabase-Free-for-all):
- Opel/Vauxhall codes are stored in a database
- The serial number is the lookup key
- No public algorithm exists - it's a proprietary calculation

## Opel Radio Models & Serial Locations

| Model | Serial Location |
|-------|-----------------|
| CD30 MP3 | Radio display, press 1+5 while powered off |
| CD70 | Menu > Settings > Device Info |
| DVD90 Navi | Navigation system menu |
| CD400 | Radio front panel |
| IntelliLink | On-screen display |

## Code Entry Procedure

1. Turn ignition to ACC/ON position
2. Turn radio on (shows LOCKED)
3. Wait for "CODE" or enter wrong code 3 times
4. Enter 4-digit code using station preset buttons
5. Code confirmed with beep or display change

## Source References
- https://www.code-radio.com/radio-code/opel
- https://mhhauto.com/Thread-RadioCodeDatabase-Free-for-all
- https://www.carstereocode.com/unlock.php?mk=28

## Notes
- No public offline algorithm available
- Codes stored in radio EEPROM, not calculated from serial
- Opel uses GM branding, Vauxhall is the UK equivalent (same systems)
- Some newer IntelliLink systems require dealer-level programming
