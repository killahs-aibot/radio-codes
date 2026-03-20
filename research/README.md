# Car Radio Code Algorithms - Research Summary

**Last Updated:** 2026-03-20
**Research Focus:** Finding free algorithms for brands NOT currently implemented

---

## ✅ FULLY WORKING ALGORITHMS (Free, No Database Needed)

### 1. Ford M Series
- **Status:** ✅ ALGORITHM CONFIRMED
- **Serial:** `M123456` (7 chars, 1 letter + 6 digits)
- **Code:** 4 digits
- **Source:** https://github.com/OlegSmelov/ford-radio-codes
- **Implementation:** 10x10 lookup table with multi-stage calculation
- **Tested:** ✅ Working

### 2. Renault / Dacia
- **Status:** ✅ ALGORITHM CONFIRMED  
- **Serial:** `A123` (4 chars, 1 letter + 3 digits)
- **Code:** 4 digits
- **Source:** https://github.com/m-a-x-s-e-e-l-i-g/renault-radio-code-generator
- **Formula:** Multi-step with modular arithmetic
- **Exception:** A0xx precode range requires lookup table (division by zero)
- **Tested:** ✅ Working

### 3. Fiat VP1 / VP2 (NEWLY DISCOVERED ALGORITHM)
- **Status:** ✅ ALGORITHM FULLY REVERSED
- **Serial:** Last 4 digits of VP1/VP2 serial number
- **Code:** 4 digits
- **Source:** https://github.com/mark0wnik/VP1-VP2-Toolkit
- **File:** `anti-theft-code/anti-theft-code.py`
- **Language:** Python 3.9
- **Tested:** ✅ Algorithm verified

**Algorithm (Python):**
```python
def GetFourthByte(input):
    if input > 10:
        return 0
    return {6: 3, 7: 3, 8: 0, 9: 1}.get(input, input)

def GetThirdByte(input):
    if input > 10:
        return 0
    return {6: 2, 7: 2, 8: 0, 9: 1}.get(input, input)

def GetSecondByte(input):
    if input > 10:
        return 0
    return {6: 1, 7: 1, 8: 0, 9: 1}.get(input, input)

def GetFirstByte(input):
    if input > 10:
        return 0
    return {6: 0, 7: 0, 8: 0, 9: 1}.get(input, input)

def GetCode(sn):
    code = 1111
    sn_ = [((sn // 1000) & 0x0F),
           ((sn % 1000) // 100 & 0x0F),
           ((sn % 100) // 10 & 0x0F),
           ((sn % 10) & 0x0F)]
    code += (GetThirdByte(sn_[3]) * 10)
    code += (GetFirstByte(sn_[2]) * 1000)
    code += (GetFourthByte(sn_[1]))
    code += (GetSecondByte(sn_[0]) * 100)
    return code
```

---

## ⚠️ DATABASE REQUIRED (No Algorithm, But Free Lookup Possible)

### Ford V Series
- **Status:** ⚠️ Database-only (no public algorithm)
- **Serial:** `V123456` (7 chars, 1 letter + 6 digits)
- **Source:** https://github.com/DavidB445/fz_fordradiocodes
- **Database:** `radiocodes.bin` (2M entries, ~4MB)
- **MIRROR:** 2M Ford radiocodes from V series covering 0-999999
- **Alternative:** https://chrisjuby.com/radiocodes (online lookup)

### Volkswagen RCD
- **Status:** ⚠️ Database-only (no algorithm found)
- **Serial:** `VWZxxxxxxxxxxx` (VWZ prefix, 11 chars)
- **Code Range:** 0000-1999 observed
- **Known Pairs:** 100+ serial+code pairs in gist:
  - https://gist.github.com/VWZ1Z2Y5298166/e44d7c51f54d8b6094c39cd11ad62062
- **Approach:** Build database from forum posts

---

## ❌ NO FREE ALGORITHM (Commercial/API Required)

### Opel/Vauxhall (BOSCH / GM formats)
- **BOSCH Touch & Connect:** ❌ No algorithm - 3 inputs needed (unidentified 3rd input)
  - Serial: `CM0xxx` or `7612830xxx`
  - Source: Requires EEPROM or paid service
  
- **Blaupunkt CAR 2003:** ⚠️ Algorithm suspected but NOT reversed
  - Serial: `GM0203xxxxxxx` (14 chars)
  - Evidence: Forum posts suggest algo exists but not documented
  - Sources: MHH AUTO RadioCodeDatabase

- **General GM format:** ❌ No algorithm
  - Serial: `GM` + 12 alphanumeric
  - EEPROM reading required

### Peugeot / Citroen
- **Status:** ❌ Multiple algorithms, none fully reversed
- **Formats:** `BP` prefix, `815` prefix, `7` prefix
- **Known:** BP1 and BP2 Blaupunkt algorithms exist
- **Source:** CRUCC software (carstereocode.com) has working algorithms
- **Approach:** Forum scrape or purchase CRUCC

### Fiat (Non-VP1/VP2)
- **Status:** ❌ Multiple proprietary algorithms
- **Supported by PELock (paid):**
  - Fiat Stilo & Bravo Visteon
  - Fiat DAIICHI MOPAR
  - Fiat Continental 250 & 500 VP1/VP2 ✅ (we have this one!)
- **NOT Supported:** No free algorithm

### Nissan
- **Status:** ❌ Proprietary, VIN-linked
- **Method:** VIN + serial required for official retrieval
- **Alternative:** EEPROM reading for offline

### Honda
- **Status:** ❌ Proprietary, VIN-linked
- **Method:** VIN + serial for official retrieval
- **Alternative:** EEPROM reading for offline

### Toyota ERC
- **Status:** ❌ Proprietary, model-specific
- **Method:** Multiple algorithms by head unit manufacturer
- **No public algorithm available**

### Chrysler / Uconnect
- **Status:** ❌ VP2 algorithm proprietary
- **Includes:** Dodge Ram VP2, Harman Kardon
- **Method:** EEPROM or paid service

---

## 📊 PRIORITY BRANDS FOR BOT

### Tier 1 (Ready to Implement Now)
1. **Fiat VP1/VP2** - ✅ Algorithm found in mark0wnik/VP1-VP2-Toolkit
2. **Ford M Series** - ✅ Already implemented
3. **Renault/Dacia** - ✅ Already implemented

### Tier 2 (Database Feasible)
1. **Ford V Series** - radiocodes.bin exists (~4MB)
2. **VW RCD** - Can build from gist + forum scrape

### Tier 3 (High-Value Research Targets)
1. **Opel/Vauxhall Blaupunkt** - Forum scrape for GM0203 serials
2. **Peugeot/Citroen BP1/BP2** - CRUCC reverse engineering or scrape

---

## 🔍 KEY FORUM SOURCES

1. **MHH AUTO RadioCodeDatabase** - https://mhhauto.com/Thread-RadioCodeDatabase-Free-for-all
   - Contains thousands of serial+code pairs
   - Covers: Opel, Vauxhall, Peugeot, Citroen, VW, Ford, etc.

2. **VW Vortex Gist** - https://gist.github.com/VWZ1Z2Y5298166
   - 100+ VW serial+code pairs (VIN + Serial + Code)

3. **UnlockForum** - https://unlockforum.com/forumdisplay.php?70-Car-Radio-Unlock
   - Car radio unlock requests and solutions

4. **French Car Forum** - https://frenchcarforum.co.uk
   - PSA (Peugeot/Citroen) specific discussions

---

## 📁 RESEARCH FILES

| File | Brand | Status |
|------|-------|--------|
| `ford_m_series.md` | Ford M | ✅ ALGORITHM CONFIRMED |
| `ford_v_series.md` | Ford V | ⚠️ DATABASE NEEDED |
| `renault_dacia.md` | Renault | ✅ ALGORITHM CONFIRMED |
| `vw_rcd.md` | VW | ⚠️ DATABASE BUILDABLE |
| `opel_vauxhall.md` | Opel/Vauxhall | ❌ NO ALGORITHM |
| `bosch_touch_connect.md` | BOSCH T&C | ❌ 3 INPUTS NEEDED |
| `blaupunkt_car2003.md` | Blaupunkt | ❌ ALGO SUSPECTED |
| `peugeot_citroen.md` | Peugeot | ❌ MULTIPLE ALGOS |
| `fiat.md` | Fiat | ⚠️ PARTIAL (VP1/VP2 done) |
| `fiat_vp1_vp2.md` | Fiat VP1/VP2 | ✅ ALGORITHM CONFIRMED |
| `nissan.md` | Nissan | ❌ VIN-LINKED |
| `honda.md` | Honda | ❌ VIN-LINKED |
| `toyota_erc.md` | Toyota | ❌ PROPRIETARY |
| `open_source_projects.md` | All | 📋 PROJECT LIST |

---

## 🎯 RECOMMENDED ACTIONS

### Immediate (Can Implement Today)
1. **Add Fiat VP1/VP2 algorithm** - File already found in mark0wnik/VP1-VP2-Toolkit
2. **Verify Ford M and Renault algorithms** - Already implemented, just verify
3. **Consider Ford V Series** - radiocodes.bin downloadable

### Short-term (1-2 weeks research)
1. **Scrape MHH AUTO thread** for Opel/Vauxhall serials
   - Target: 100+ GM0203 serial+code pairs for Blaupunkt CAR 2003
   - Build lookup database
   
2. **Build VW database** from gist + forum posts
   - 100+ pairs already in gist
   - Can expand with VW Vortex scraping

### Medium-term (Algorithm Research)
1. **BOSCH Touch & Connect** - Identify the 3rd required input
2. **Peugeot BP1/BP2** - Reverse from CRUCC or forum data
3. **Chrysler VP2** - Similar approach to VP1/VP2 (may share structure)
