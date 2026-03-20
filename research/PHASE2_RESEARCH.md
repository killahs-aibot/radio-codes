# RadioUnlock — Phase 2 Algorithm Research Report

**Researcher:** Tam (RadioUnlock Lead Researcher)
**Date:** 2026-03-20
**Phase:** 2 — Deep Dive into Unverified/Unsupported Brands
**Repo:** https://github.com/killahbtc/radio-codes

---

## Executive Summary

After deep investigation of car radio code algorithms across 15+ brands, the findings confirm that **genuinely open-source radio code algorithms are extremely rare**. Only **3 brands** have publicly confirmed, test-vector-verified formulas:

1. **Ford M Series** — 10×10 lookup table, multi-stage transform
2. **Renault/Dacia** — Precode modular arithmetic formula
3. **Fiat VP1/VP2** — Nibble-extract + position-based lookup tables

Everything else is either: (a) a commercial paid API, (b) a database lookup, (c) EEPROM-reading-only, or (d) a dealer-only system. The automotive radio code industry is deliberately obfuscated — this is by design, as it generates continuous revenue for dealers and third-party code services.

---

## ✅ VERIFIED ALGORITHMS (100% Confirmed, Working)

### 1. Ford M Series — CONFIRMED ✅
**Source:** https://github.com/OlegSmelov/ford-radio-codes
**Status:** FULLY REVERSED — 5/5 test vectors pass

Serial format: `M123456` (1 letter + 6 digits)
Code: 4 digits

Uses a 10×10 lookup table with 4 chained transformations.

**Already implemented in:** `src/radiocodes/algorithms/ford_m.py` ✅

---

### 2. Renault / Dacia — CONFIRMED ✅
**Source:** https://gist.github.com/yne/d6dad90416727c2e027774857233524f
**Status:** FULLY REVERSED — 13/13 test vectors pass

Serial format: `A123` (1 letter + 3 digits)
Code: 4 digits

Uses precode modular arithmetic with ASCII values.

**Already implemented in:** `src/radiocodes/algorithms/renault.py` ✅

---

### 3. Fiat VP1 / VP2 — CONFIRMED ✅
**Source:** https://github.com/mark0wnik/VP1-VP2-Toolkit
**Status:** FULLY REVERSED — 5/5 test vectors pass

Serial: Last 4 digits of serial number (0-9999)
Code: 4 digits

Uses nibble extraction with special handling for digits 6-9.

**Already implemented in:** `src/radiocodes/algorithms/fiat.py` ✅

---

## ⚠️ DATABASE-ONLY IMPLEMENTATIONS (No Formula Exists Publicly)

### 4. Ford V Series — Binary Database ✅
**Source:** https://github.com/DavidB445/fz_fordradiocodes
**Status:** Database lookup (radiocodes.bin), NOT a formula

Serial format: `V123456` (1 letter + 6 digits)
Code: 4 digits

Requires pre-computed radiocodes.bin (2M entries).

**Already implemented in:** `src/radiocodes/algorithms/ford_m.py` (FordVAlgorithm) + `data/ford_radiocodes.bin` ✅

---

### 5. VW / Audi / Seat / Skoda — Database Lookup ⚠️
**Source:** https://gist.github.com/VWZ1Z2Y5298166/e44d7c51f54d8b6094c39cd11ad62062
**Status:** NO ALGORITHM EXISTS — Forum pairs database (158 entries)

Serial format: 14-character (e.g., `VWZ5Z7B5013069`)
Code: 4 digits (range 0000-1999)

The VW RCD algorithm is proprietary and has NOT been publicly reversed. The radiocode appears to be stored directly in EEPROM, not derived from serial.

**Already implemented in:** `src/radiocodes/algorithms/vw_rcd.py` + `data/forum_pairs.csv` ✅

---

### 6. Vauxhall / Opel — Database Lookup ⚠️
**Status:** NO ALGORITHM — Multiple manufacturers, database approach

Serial formats: `GM0203...`, `GM0204...`, `GM030M...`, `GM0400...`, `CM0141...`
Code: 4 digits

Different radio manufacturers (Blaupunkt, Delphi, Bosch) = different codes. No unified algorithm.

**Already implemented in:** `src/radiocodes/algorithms/vauxhall.py` + `data/forum_pairs.csv` ✅

---

## ❌ UNVERIFIED/UNSUPPORTED BRANDS — Detailed Analysis

### 7. Nissan ❌
**Status:** NO ALGORITHM — VIN-linked, proprietary

**What we know:**
- Serial format: 12 hex characters (e.g., `CY16C-1234567`)
- Official portal: https://radio-navicode.nissan.com/ (FREE, VIN-linked)
- Some units use Blaupunkt BP serial format → may relate to Blaupunkt algorithm

**Current repo formula:** `code = ((sum_of_hex_values * 3) + 7777) % 10000` — **UNVERIFIED, likely wrong**

**Recommendation:** 
- Use official Nissan portal (free)
- For EEPROM: Read 24Cxx chip, code stored at known addresses
- Priority for reverse engineering: Nissan Connect units with BP serial prefix

**Sources:**
- https://radio-navicode.nissan.com/ (official free portal)
- PELock commercial: https://www.pelock.com/products/nissan-glove-box-pin-code-calculator

---

### 8. Peugeot / Citroën ❌
**Status:** NO ALGORITHM — Multiple radio manufacturers

**What we know:**
- Serial formats: `BPxxxxxxxxxxxx` (Blaupunkt), `815xxxxxxxxxxx` (Valeo), `7xxxxxxxxxxx` (Siemens)
- Models: RT3, RT4, RNEG, MyWay, WipNav, WipCom
- One known vector: `BP2 775(S) 9452352` → `2893` (Citroen Algo 1)

**Current repo formula:** `((total ^ 0x1357) + 5000) % 10000` — **UNVERIFIED**

**Recommendation:**
- Collect 50+ confirmed pairs for BP format first
- The CRUCC software (carstereocode.com) reportedly has reverse-engineered algorithms
- EEPROM reading is the reliable offline method

**Sources:**
- https://www.pelock.com/products/peugeot-citroen-radio-unlock-code-calculator (commercial)
- MHH AUTO forum Peugeot radio code threads

---

### 9. Alfa Romeo ❌
**Status:** NO ALGORITHM — Shares Fiat architecture

**What we know:**
- Many Alfa Romeo units use the same Blaupunkt BP platform as Fiat
- Try Fiat VP1/VP2 algorithm for BP-prefix serials
- Models: Connect, Nav+, Giulietta, MiTo

**Current repo:** Placeholder, no formula — **UNVERIFIED**

**Recommendation:**
- Fiat VP1/VP2 algorithm is the best starting point for BP-prefix serials
- For other formats: EEPROM reading required

**Sources:**
- Fiat VP1/VP2 algorithm works for some Alfa Romeo units
- https://github.com/mark0wnik/VP1-VP2-Toolkit (includes Alfa Romeo support)

---

### 10. Chrysler / Dodge / Jeep ❌
**Status:** NO ALGORITHM — Multiple head unit types

**What we know:**
- VP2 head units (Harman Kardon) in Dodge Ram: Serial format `TXPQNxxxxxxxx` — use last 4 digits
- Jeep Cherokee: Supplier code starts with `17719`, serial = 14 chars
- Uconnect 8.4": NAVCODE format (paid service)

**Known format:** VP2 serial starts with `TXPQN` + 9 letters/digits — last 4 digits are used

**Recommendation:**
- For VP2 (Dodge Ram Harman Kardon): Extract last 4 digits, try Fiat VP1/VP2 algorithm as starting point
- For Jeep Cherokee: Supplier code `17719` + 14-char serial → paid service
- For Uconnect: EEPROM or paid service

**Sources:**
- https://www.pelock.com/products/chrysler-dodge-ram-uconnect-harman-kardon-radio-code (commercial)
- https://www.pelock.com/products/jeep-cherokee-radio-unlock-code-calculator-generator (commercial)

---

### 11. Jaguar / Land Rover ❌
**Status:** NO ALGORITHM — Alpine-based units

**What we know:**
- Serial: Last 5 digits only (5-char numeric from 10-char serial)
- Code: 4 digits
- Units are Alpine-based
- Codes are often printed on a security card in glovebox

**Recommendation:**
- Check glovebox security card first
- For Alpine head units: Some success with EEPROM reading
- PELock commercial: https://www.pelock.com/products/jaguar-alpine-car-radio-unlock-code-calculator

**Sources:**
- https://www.pelock.com/products/jaguar-alpine-car-radio-unlock-code-calculator (commercial)
- Security card in vehicle documents

---

### 12. Volvo ❌
**Status:** NO ALGORITHM — Various head units

**What we know:**
- Models: HU-603, HU-605, HU-609, RTI, ICE
- Serial formats vary by head unit manufacturer (Philips, Grundig, Harman Kardon)
- No public algorithm found on GitHub, forums, or open source projects

**Recommendation:**
- EEPROM reading is the reliable method
- Check vehicle documents for security card
- Some Volvo units use the same algorithm as Ford (when head unit shared)

**Sources:**
- Volvo forums (various)
- PELock commercial (likely)
- No GitHub repositories found for Volvo radio code algorithms

---

### 13. Honda ✅ (Official Portal)
**Status:** FREE OFFICIAL PORTAL EXISTS

**What we know:**
- Official free portal: https://radio-navicode.honda.com/
- Also: https://radio-navicode.acura.com/
- Serial: 5-10 characters (press SETUP to display)
- Code: 5 digits
- Requires VIN + serial

**Already implemented in:** `src/radiocodes/algorithms/honda.py` (shows portal link) ✅

**Recommendation:**
- Portal covers most cases — direct users there
- EEPROM for offline scenarios
- No algorithm to reverse — VIN-linked proprietary system

---

### 14. Toyota / Lexus ❌
**Status:** ERC SYSTEM — Dealer-only

**What we know:**
- ERC (Emergency Radio Code) = 16-character alphanumeric
- NOT the serial number — ERC is displayed via hidden menu
- To get ERC: Hold main button on nav + flash parking lights 3-4 times
- Code: 4-5 digits

**Models supported (by year):**
- 2020: NSCD-W66
- 2014: NSCP-W64, NSZA-X64T, NSZN-W64T, NSZT-W64, NSZT-Y64T, NSZT-YA4T
- 2012: NHBA-W62G, NHBA-X62G, NHZD-W62G, NHZN-X62G, NSCP-W62, NSCT-D61D, NSLN-W62, NSZT-W62G, NSZT-Y62G
- And many more (see full list in Toyota research doc)

**Recommendation:**
- Dealer or independent garage with Toyota SDP (~£10-20)
- EEPROM reading (CH341A + full chip scan)
- No free algorithm exists

**Already implemented in:** `src/radiocodes/algorithms/toyota.py` ✅ (shows dealer/EEPROM options)

---

### 15. Mazda ❌
**Status:** NO ALGORITHM — Mazda Connect system

**What we know:**
- Uses MazdaConnect system (various head units)
- Serial format: Varies by model
- No public algorithm found on GitHub or forums

**Recommendation:**
- Check vehicle documents for security card
- EEPROM reading for offline
- Some shared architecture with Ford (common head unit supplier)

**Sources:**
- Mazda owner forums
- EEPROM reading guides
- No GitHub repositories found for Mazda radio code algorithms

---

### 16. Mitsubishi ❌
**Status:** NO ALGORITHM

**What we know:**
- Uses MMCS (Multi Media Communication System) on some models
- No public algorithm found

**Recommendation:** EEPROM reading

---

### 17. Suzuki ❌
**Status:** NO ALGORITHM

**What we know:**
- Various head units depending on model year
- No public algorithm found

**Recommendation:** EEPROM reading, check vehicle documents

---

### 18. Hyundai / Kia ❌
**Status:** NO ALGORITHM

**What we know:**
- Various head units
- Some models use the same head unit suppliers as other brands
- No public algorithm found

**Recommendation:** EEPROM reading or dealer

---

### 19. BMW ❌
**Status:** NO ALGORITHM — High priority target

**What we know:**
- Business CD (MF2xx), Munich R-series, MK4, etc.
- Serial format: `F123456789` or `6 123 456`
- Suspected XOR or simple checksum but NOT confirmed
- EEPROM reading works for ALL BMW models

**Recommendation:**
- **HIGH PRIORITY** for algorithm research
- Collect serial+code pairs from forums
- PCB dumps + analysis could reveal algorithm
- PELock commercial: https://www.pelock.com/products/bmw-radio-unlock-code-calculator

**Sources:**
- MHH AUTO BMW radio code threads
- BMW forums
- PELock commercial

---

### 20. Mercedes-Benz ❌
**Status:** NO ALGORITHM

**What we know:**
- COMAND NTG1-4, Audio 20, Becker variants
- No public algorithm
- EEPROM reading common

**Sources:**
- Mercedes-Benz service forums
- PELock commercial

---

## 🔍 BLAUPUNKT CROSS-BRAND ANALYSIS

Blaupunkt is a MAJOR radio supplier to multiple automotive brands. Finding a Blaupunkt algorithm could unlock multiple brands simultaneously.

### Known Blaupunkt Serial Formats:
| Brand | Serial Prefix | Status |
|-------|--------------|--------|
| Fiat | BP... | VP1/VP2 algorithm works ✅ |
| Peugeot/Citroën | BP... | Unknown algorithm ❌ |
| Nissan | BP... | May share Fiat algorithm ❌ |
| Opel/Vauxhall | GM0203... | May share Blaupunkt algo ❌ |
| Jaguar | Alpine-based | Not Blaupunkt ❌ |
| Ford (some) | Various | Ford algorithm works ✅ |
| Renault (some) | Blaupunkt-based | Renault algorithm works ✅ |

### Blaupunkt Model References:
- CAR2003 (Opel/Vauxhall: GM0203...)
- CAR2004 (Opel: GM0204...)
- CAR300 (Opel: GM030M...)
- CAR400 (Opel: GM0400...)
- BP1, BP2 (Peugeot/Citroën)

**Research needed:** Contact the CRUCC project (carstereocode.com) or reverse engineer a Blaupunkt BP chip dump to find the universal algorithm.

---

## 📊 ALGORITHM PRIORITY MATRIX

| Brand | Priority | Difficulty | Approach | Notes |
|-------|----------|------------|----------|-------|
| Ford M | DONE ✅ | Easy | Formula | Fully reversed |
| Ford V | DONE ✅ | Medium | Binary DB | radiocodes.bin |
| Renault | DONE ✅ | Easy | Formula | Fully reversed |
| Fiat VP1/VP2 | DONE ✅ | Medium | Formula | Fully reversed |
| Honda | DONE ✅ | N/A | Portal | Free official portal |
| Toyota | DONE ✅ | N/A | Dealer/EEPROM | ERC system |
| VW/Audi/Seat | PARTIAL | Hard | Database | 158 pairs, no algo |
| Vauxhall/Opel | PARTIAL | Hard | Database | Multiple formats |
| Peugeot/Citroën | 🔴 HIGH | Hard | Database | Collect pairs first |
| Nissan | 🟡 MED | Hard | Portal first | Portal free, algo guess |
| Alfa Romeo | 🟡 MED | Medium | Fiat-based | Try VP1/VP2 for BP |
| Chrysler/Dodge | 🟡 MED | Hard | Database | VP2 last-4 approach |
| Jaguar/LR | 🟡 MED | Hard | EEPROM | Alpine-based |
| BMW | 🔴 HIGH | Hard | EEPROM/Research | High demand |
| Volvo | 🟡 MED | Hard | EEPROM | No algo found |
| Mazda | 🟡 MED | Hard | EEPROM | May share Ford algo |
| Mercedes | 🟢 LOW | Hard | EEPROM | EEPROM sufficient |
| Mitsubishi | 🟢 LOW | Hard | EEPROM | No demand |
| Suzuki | 🟢 LOW | Hard | EEPROM | No demand |
| Hyundai/Kia | 🟢 LOW | Hard | EEPROM | No demand |

---

## 📁 SOURCE REFERENCE TABLE

| Brand | Open Source | Commercial API | EEPROM |
|-------|-------------|----------------|--------|
| Ford M | ✅ OlegSmelov | PELock | ✅ |
| Ford V | ✅ DB | PELock | ✅ |
| Renault | ✅ yne gist | PELock | ✅ |
| Fiat VP1/VP2 | ✅ mark0wnik | PELock | ✅ |
| VW/Audi | ❌ forum DB only | PELock | ✅ |
| Opel/Vauxhall | ❌ forum DB only | PELock | ✅ |
| Peugeot | ❌ | PELock | ✅ |
| Nissan | ❌ portal only | PELock | ✅ |
| Honda | ✅ portal | PELock | ✅ |
| Toyota | ❌ | PELock | ✅ |
| Alfa Romeo | ❌ | PELock | ✅ |
| Chrysler/Dodge | ❌ | PELock | ✅ |
| Jaguar/LR | ❌ | PELock | ✅ |
| BMW | ❌ | PELock | ✅ |
| Volvo | ❌ | ? | ✅ |
| Mazda | ❌ | ? | ✅ |
| Mercedes | ❌ | ? | ✅ |

---

## 🎯 RECOMMENDED NEXT STEPS

### Immediate (This Week)

1. **Fix unverified formulas in repo**
   - Remove or clearly mark as UNVERIFIED the following algorithms:
     - Nissan (formula is a guess)
     - Peugeot (formula is a guess)
     - Alfa Romeo (no formula)
     - Chrysler (no formula)
     - Jaguar (no formula)
   - These should either raise `NotImplementedError` or display strong warnings

2. **Expand VW RCD database**
   - Scrape more forum pairs from vwvortex.com
   - Target: 500+ pairs from current 158
   - Build a scraper for vwvortex.com radio code threads

3. **Expand Vauxhall/Opel database**
   - Target MHH AUTO thread for GM0203 pairs
   - Collect 500+ confirmed pairs

### Short-term (2-4 Weeks)

4. **Research Blaupunkt BP algorithm**
   - Priority: This could unlock Peugeot, Nissan, and Opel simultaneously
   - Approach: Get a BP chip dump, reverse engineer the algorithm
   - Contact CRUCC project (carstereocode.com) for collaboration

5. **Research Chrysler VP2**
   - Dodge Ram VP2 (Harman Kardon) is high demand
   - Try Fiat VP1/VP2 algorithm on VP2 last-4-digits format
   - Collect 20+ confirmed pairs to verify

6. **Honda/Acura portal integration**
   - Current implementation shows the portal link
   - Could add optional web scraping to auto-retrieve code
   - But VIN required = would need user input

### Medium-term (1-3 Months)

7. **BMW research**
   - High demand, no open source solution
   - Collect PCB dumps + serial+code pairs
   - Target: Business CD (MF2xx) series

8. **Ford TravelPilot (navigation radios)**
   - Separate from M/V series
   - PELock shows support: Ford TravelPilot EX, FX & NX
   - Research if Flipper Zero app covers these

---

## 🔑 KEY INSIGHT: The EEPROM Shortcut

For ANY brand without an algorithm, EEPROM reading is the universal solution:

**CH341A + flashrom workflow:**
1. Remove radio from vehicle
2. Identify EEPROM chip (usually 24C01, 24C02, 24C04, 24C08)
3. Connect CH341A programmer
4. Run `flashrom -r radio_dump.bin`
5. Search dump for 4-digit code patterns
6. Some chips store code at known addresses:
   - VW RCD: typically `0x00-0x03`
   - Ford M/V: varies by PCB revision
   - Blaupunkt CAR2003: reported at `0x1A0-0x1A3`

**This approach works for ALL brands when no algorithm exists.**

---

## 📚 GITHUB REPOSITORIES FOUND

1. **OlegSmelov/ford-radio-codes** — Ford M algorithm ✅
2. **DavidB445/fz_fordradiocodes** — Ford V binary database ✅
3. **mark0wnik/VP1-VP2-Toolkit** — Fiat VP1/VP2 algorithm ✅
4. **yne/gist (d6dad9...)** — Renault algorithm ✅
5. **m-a-x-s-e-e-l-i-g/renault-radio-code-generator** — Renault JS ✅
6. **ojacquemart/renault-radio-code-list** — 23K test vectors ✅
7. **PELock/Radio-Code-Calculator-Python** — Commercial SDK
8. **PELock/Radio-Code-Calculator-JavaScript** — Commercial SDK
9. **PELock/Radio-Code-Calculator-PHP** — Commercial SDK
10. **killahbtc/radio-codes** — This project ⭐

---

## 🏁 CONCLUSION

The car radio code ecosystem is deliberately closed. Only 3 brands (Ford M, Renault, Fiat VP1/VP2) have publicly confirmed open-source algorithms. Everything else is either:
- A paid commercial service (PELock and competitors)
- A database lookup (VW, Vauxhall/Opel)
- An EEPROM solution (universal but requires hardware)

**The best strategy for RadioUnlock:**
1. Perfect the 3 verified algorithms (Ford M, Renault, Fiat VP1/VP2)
2. Build database coverage for VW and Vauxhall
3. For all other brands: Provide clear guidance to official portals + EEPROM workflow
4. Never claim to have an algorithm when one doesn't exist publicly

**PELock is the de facto standard** — their commercial SDK covers 15+ brands. Studying their product pages reveals what formats and serial patterns are used, even if the algorithms themselves aren't open source.

---

*End of Phase 2 Research Report*
*Tam — RadioUnlock Research Division*
*2026-03-20*
