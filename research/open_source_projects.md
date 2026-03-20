# Open Source Radio Code Projects

## Summary

This document lists all open source projects found during research for car radio code algorithms.

## Projects with Working Algorithms

### 1. Ford M Series (COMPLETE)
**Repository:** https://github.com/OlegSmelov/ford-radio-codes
**License:** MIT
**Language:** Node.js
**Status:** ✅ Algorithm fully reversed - lookup table implementation works

### 2. Ford V Series (DATABASE)
**Repository:** https://github.com/DavidB445/fz_fordradiocodes
**Flipper Zero app:** Ford Radio 'M' & 'V' Unlock Code Generator
**License:** MIT
**Language:** C (Flipper Zero), Python
**Status:** ✅ Uses pre-computed radiocodes.bin database

### 3. Renault/Dacia (COMPLETE)
**Repositories:**
- https://gist.github.com/yne/d6dad90416727c2e027774857233524f
- https://github.com/m-a-x-s-e-e-l-i-g/renault-radio-code-generator
- Original by: https://github.com/lucasg
**License:** MIT
**Language:** JavaScript, Python
**Status:** ✅ Fully working formula-based algorithm

### 4. Fiat VP1/VP2
**Repository:** https://github.com/mark0wnik/VP1-VP2-Toolkit
**Description:** Unlock code calculator AND CAN emulator for VP1/VP2 radios
**License:** Not specified
**Language:** Not verified
**Status:** ⚠️ Contains working code (algorithm not analyzed in detail)

## Commercial SDKs (API Required)

### PELock Radio Code Calculator
**Repository:** https://github.com/PELock/Radio-Code-Calculator-Python
**Also:** JavaScript, PHP versions
**License:** Commercial (paid API key required)
**Supports:**
- Renault & Dacia
- Toyota ERC
- Ford M Serial
- Ford V Serial
- Ford TravelPilot EX, FX & NX
- Chrysler Dodge Ram VP2
- Fiat Stilo & Bravo Visteon
- Fiat DAIICHI MOPAR
- Fiat 250 & 500 VP1/VP2
- Nissan Glove Box PIN
- Jeep Cherokee
- Jaguar Alpine
- Eclipse ESN
- Many more...

## Algorithms NOT Reversed (No Open Source)

### ❌ Volkswagen RCD
- No public algorithm
- Lookup databases exist (forum posts)
- EEPROM reading required for accurate results

### ❌ Opel/Vauxhall
- No public algorithm
- Database-driven approach
- EEPROM reading common method

### ❌ Peugeot/Citroen
- Multiple algorithms (Blaupunkt BP1, BP2, etc.)
- No universal open source solution
- CRUCC software available (carstereocode.com)

### ❌ Fiat (General)
- Multiple manufacturers (Visteon, DAIICHI, MOPAR)
- VP1/VP2 only open source
- Paid services for others

### ❌ Nissan
- No algorithm
- VIN-based official portal only
- EEPROM reading for offline

### ❌ Honda
- No algorithm
- VIN + serial required for official retrieval
- EEPROM reading possible

### ❌ Toyota ERC
- No public algorithm
- Third-party calculators use private algorithms
- Different for each head unit manufacturer

## Gist/Forums with Code Examples

1. **Ford M Series Gist:** https://gist.github.com/4ndrej/b252c4ec3efa49d2b7b03c704c1289e3

2. **VW Codes Database:** https://gist.github.com/VWZ1Z2Y5298166/e44d7c51f54d8b6094c39cd11ad62062

3. **Renault Code:** https://gist.github.com/yne/d6dad90416727c2e027774857233524f

4. **Chris Juby Ford V Series:** https://chrisjuby.com/radiocodes (online lookup, not code)

## Research Notes

### Algorithm Difficulty Ratings

| Brand | Difficulty | Reason |
|-------|-----------|--------|
| Ford M | Easy | Lookup table fully reversed |
| Renault | Easy | Simple formula discovered |
| Ford V | Medium | Requires database (2M entries) |
| VW | Hard | Algorithm not reversed |
| Peugeot/Citroen | Hard | Multiple vendor algorithms |
| Fiat (VP1/VP2) | Medium | Open source toolkit exists |
| Opel/Vauxhall | Hard | No algorithm, database only |
| Nissan | Very Hard | Proprietary, VIN-linked |
| Honda | Very Hard | Proprietary, VIN-linked |
| Toyota ERC | Very Hard | Proprietary, model-specific |

### Recommendations for Bot Implementation

1. **Implement fully working algorithms first:**
   - Ford M Series ✅
   - Renault/Dacia ✅

2. **Add database lookup:**
   - Ford V Series (use radiocodes.bin)
   - VW (use forum database or generate)

3. **For others:**
   - Consider PELock SDK integration (paid)
   - Or direct users to official services
   - EEPROM reading guides for advanced users
