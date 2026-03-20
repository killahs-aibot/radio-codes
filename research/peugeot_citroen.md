# Peugeot / Citroen Radio Code Algorithm

## Overview
- **Brand:** Peugeot, Citroen (PSA Group)
- **Serial Formats:**
  - `BP` prefix (Blaupunkt): BP2774P9733521, BP2 775(S) 9452352
  - `815` prefix: 815BP730181889575, 815CM1234B1234567
  - `7` prefix: 7 647 301 316
- **Output Code:** 4 digits
- **Works with:** 206, 207, 306, 307, 406, Partner, C3, C4, C5, and others

## Algorithm Type
Multi-algorithm support depending on radio manufacturer and model year:
1. **Blaupunkt Algorithm 1** (BP1)
2. **Blaupunkt Algorithm 2** (BP2)  
3. **Valeo/Siemens Algorithms**
4. **Clarion C7** (PSA-specific)

## Known Algorithms

### Blaupunkt BP1/BP2 Algorithm

From French Car Forum (https://frenchcarforum.co.uk/forum/viewtopic.php?t=25908):

Example: Serial `BP2 775(S) 9452352`
- Select "Citroen Algo 1" in calculator
- Result: Code `2893`

The Blaupunkt algorithm uses the serial number to look up or calculate the code.
Different variants exist for different model years.

### Algorithm Steps (Blaupunkt)

```python
def blaupunkt_peugeot_citroen(serial, algo=1):
    """
    Blaupunkt radio code algorithm for Peugeot/Citroen
    
    Note: Exact algorithm not publicly reversed. This is a placeholder
    showing the structure based on known implementations.
    """
    # Remove spaces and non-alphanumeric
    serial = serial.replace(' ', '').replace('(', '').replace(')', '')
    
    if algo == 1:
        # Algo 1 - for certain BP serial formats
        # Uses lookup table similar to Ford M-Series
        pass
    elif algo == 2:
        # Algo 2 - for BP2 variants
        pass
    
    return None  # Algorithm not reversed
```

## Known Test Vector

| Serial Format | Algorithm | Code | Source |
|---------------|-----------|------|--------|
| BP2 775(S) 9452352 | Citroen Algo 1 | 2893 | French Car Forum |

## PSA / Clarion C7

For newer PSA vehicles with Clarion C7 radio:
- Code is stored in radio's internal memory
- Retrieved via diagnostic equipment
- Cannot be calculated from serial number

## Serial Number Locations

### On Radio Label
```
BP2774P9733521
7 647 301 316
815BP730181889575
```

### Via Display (Blaupunkt)
1. Hold buttons 1 and 6 simultaneously
2. While holding, press power
3. Serial displayed (may show as security number)

### Via CAN Bus (Newer Models)
Requires dealer diagnostic equipment or aftermarket scanner.

## Source References
- https://frenchcarforum.co.uk/forum/viewtopic.php?t=25908
- https://mhhauto.com/Thread-RadioCodeDatabase-Free-for-all
- https://www.onlineradiocodes.co.uk/peugeot-radio-codes
- https://www.onlineradiocodes.co.uk/citroen-radio-code

## Online Tools
- CRUCC (Car Radio Unlock Codes) - carstereocode.com/crucc.php
- Various paid online generators

## Notes
- PSA uses multiple radio manufacturers (Blaupunkt, Clarion, Valeo, Siemens)
- Each manufacturer has different algorithm
- Pre-2000 vehicles often use simple algorithms
- Post-2000 vehicles require dealer-level code retrieval
- No universal algorithm exists for all Peugeot/Citroen radios
