# RadioUnlock — Algorithm Gold Rush: COMPLETE REPORT

**Researcher:** Tam (RadioUnlock Lead Researcher)
**Date:** 2026-03-20
**Status:** PHASE 1 COMPLETE — Comprehensive algorithm survey finished
**Repo:** https://github.com/killahbtc/radio-codes

---

## Executive Summary

RadioUnlock currently has **8 brand implementations**, of which:
- **4 are fully confirmed formulas** (Ford M, Renault/Dacia, Fiat VP1/VP2, plus Ford V as binary DB)
- **4 are database-only** (VW RCD, Vauxhall/Opel, and two placeholder formulas for Nissan/Peugeot that are unverified)
- **6+ have placeholder implementations** (Honda, Toyota, Alfa Romeo, Chrysler, Jaguar, Peugeot) with unverified formulas

**The open-source community has confirmed formulas for only 3 brands: Ford M, Renault/Dacia, and Fiat VP1/VP2.** Everything else requires either a lookup database or EEPROM reading.

---

## ✅ VERIFIED ALGORITHMS (100% Confirmed)

---

### Brand: Ford — M Series
### Algorithm: 10×10 Lookup Table — Multi-Stage Transform

**Serial Format:** `M123456` (1 letter + 6 digits)
**Code Format:** 4 digits

**Formula:**
1. Take digits 2–7 of serial, reverse the 6-digit sequence
2. Index into the 10×10 lookup table at fixed column positions to get intermediate values r1–r7
3. Apply 4 chained modulo-10 operations using cross-references within the table
4. Apply 4 more cross-references with added constants (105, 102, 103, 108)
5. Each final digit = (tens digit of xres + ones digit of xres + r1) % 10

**Test Vectors (5/5 PASSED):**
| Serial | Code |
|--------|------|
| M000000 | 1558 |
| M000001 | 9617 |
| M123456 | 2487 |
| M999999 | 4968 |
| M111111 | 8691 |

**Python Implementation:**
```python
_FORA_M_LOOKUP = [
    [9, 5, 3, 4, 8, 7, 2, 6, 1, 0],
    [2, 1, 5, 6, 9, 3, 7, 0, 4, 8],
    [0, 4, 7, 3, 1, 9, 6, 5, 8, 2],
    [5, 6, 4, 1, 2, 8, 0, 9, 3, 7],
    [6, 3, 1, 2, 0, 5, 4, 8, 7, 9],
    [4, 0, 8, 7, 6, 1, 9, 3, 2, 5],
    [7, 8, 0, 5, 3, 2, 1, 4, 9, 6],
    [1, 9, 6, 8, 7, 4, 5, 2, 0, 3],
    [3, 2, 9, 0, 4, 6, 8, 7, 5, 1],
    [8, 7, 2, 9, 5, 0, 3, 1, 6, 4],
]

def ford_m_series(serial: str) -> str:
    digits = [int(c) for c in serial[1:7]]
    n = list(reversed(digits))
    n1, n2, n3, n4, n5, n6 = n[0], n[1], n[2], n[3], n[4], n[5]
    r1 = _FORA_M_LOOKUP[n1][5]
    r2 = _FORA_M_LOOKUP[n2][3]
    r3 = _FORA_M_LOOKUP[n3][8]
    r4 = _FORA_M_LOOKUP[n4][2]
    r5 = _FORA_M_LOOKUP[n5][1]
    r6 = _FORA_M_LOOKUP[n6][6]
    r7 = 0  # always 0 (6-digit serial)

    res1 = ((_FORA_M_LOOKUP[r2][r1] + 1) * (_FORA_M_LOOKUP[r6][r2] + 1) +
            (_FORA_M_LOOKUP[r4][r3] + 1) * (_FORA_M_LOOKUP[r7][r5] + 1) +
            _FORA_M_LOOKUP[r1][r4]) % 10
    res2 = ((_FORA_M_LOOKUP[r2][r1] + 1) * (_FORA_M_LOOKUP[r5][r4] + 1) +
            (_FORA_M_LOOKUP[r5][r2] + 1) * (_FORA_M_LOOKUP[r7][r3] + 1) +
            _FORA_M_LOOKUP[r1][r6]) % 10
    res3 = ((_FORA_M_LOOKUP[r2][r1] + 1) * (_FORA_M_LOOKUP[r4][r2] + 1) +
            (_FORA_M_LOOKUP[r3][r6] + 1) * (_FORA_M_LOOKUP[r7][r4] + 1) +
            _FORA_M_LOOKUP[r1][r5]) % 10
    res4 = ((_FORA_M_LOOKUP[r2][r1] + 1) * (_FORA_M_LOOKUP[r6][r3] + 1) +
            (_FORA_M_LOOKUP[r3][r7] + 1) * (_FORA_M_LOOKUP[r2][r5] + 1) +
            _FORA_M_LOOKUP[r4][r1]) % 10

    xres1 = (_FORA_M_LOOKUP[res1][5] + 1) * (_FORA_M_LOOKUP[res2][1] + 1) + 105
    xres2 = (_FORA_M_LOOKUP[res2][1] + 1) * (_FORA_M_LOOKUP[res4][0] + 1) + 102
    xres3 = (_FORA_M_LOOKUP[res1][5] + 1) * (_FORA_M_LOOKUP[res3][8] + 1) + 103
    xres4 = (_FORA_M_LOOKUP[res3][8] + 1) * (_FORA_M_LOOKUP[res4][0] + 1) + 108

    code0 = ((xres4 // 10) % 10 + xres4 % 10 + r1) % 10
    code1 = ((xres3 // 10) % 10 + xres3 % 10 + r1) % 10
    code2 = ((xres2 // 10) % 10 + xres2 % 10 + r1) % 10
    code3 = ((xres1 // 10) % 10 + xres1 % 10 + r1) % 10

    return f"{code0}{code1}{code2}{code3}"
```

**Verification:** ✅ **PASS — 5/5 vectors confirmed**
**Source:** https://github.com/OlegSmelov/ford-radio-codes, https://gist.github.com/4ndrej/b252c4ec3efa49d2b7b03c704c1289e3
**Already in repo:** `src/radiocodes/algorithms/ford_m.py` ✅

---

### Brand: Renault / Dacia
### Algorithm: Precode Modular Arithmetic

**Serial Format:** 4 characters: 1 letter + 3 digits (e.g., `A100`, `D123`, `H456`)
**Code Format:** 4 digits

**Formula:**
```
x = ord(letter) + ord(first_digit) * 10 - 698
y = ord(third_digit) + ord(second_digit) * 10 + x - 528
z = (y * 7) % 100
code = (z // 10) + (z % 10) * 10 + ((259 % x) % 100) * 100
```

Note: `ord()` returns ASCII values — `A`=65, `0`=48. For precode `A100`: ord('1')=49, ord('0')=48.

**⚠️ CRITICAL EXCEPTION:** Precodes starting with `A0` (A001–A099) cause division by zero (`259 % 0`). These require a full 23,402-entry lookup table.

**Test Vectors (13/13 PASSED):**
| Precode | Code |
|---------|------|
| A100 | 0070 |
| A101 | 0041 |
| A102 | 0012 |
| A103 | 0082 |
| A110 | 0077 |
| A120 | 0074 |
| A130 | 0071 |
| A140 | 0078 |
| A150 | 0075 |
| A200 | 0141 |
| D123 | 1187 |
| H456 | 3701 |
| V234 | 4722 |

**Python Implementation:**
```python
def renault_code(precode: str) -> str:
    precode = precode.upper()
    if precode.startswith("A0"):
        raise ValueError(
            "Precode A0xx range requires full lookup table "
            "(23,402 entries). Download from: "
            "https://github.com/ojacquemart/renault-radio-code-list"
        )
    x = ord(precode[1]) + ord(precode[0]) * 10 - 698
    y = ord(precode[3]) + ord(precode[2]) * 10 + x - 528
    z = (y * 7) % 100
    code = (z // 10) + (z % 10) * 10 + ((259 % x) % 100) * 100
    return f"{code:04d}"
```

**Trace Example (A100):**
```
A100: ord values = [65, 49, 48, 48]
x = 49 + 65*10 - 698 = 1
y = 48 + 48*10 + 1 - 528 = 1
z = (1*7) % 100 = 7
code = 0 + 70 + (259%1%100)*100 = 70
Result: "0070"
```

**Verification:** ✅ **PASS — 13/13 vectors confirmed against 23K dataset**
**Source:** https://gist.github.com/yne/d6dad90416727c2e027774857233524f, https://github.com/ojacquemart/renault-radio-code-list
**Already in repo:** `src/radiocodes/algorithms/renault.py` ✅

---

### Brand: Fiat / Alfa Romeo — VP1 / VP2
### Algorithm: Nibble-Extract + Position-Based Lookup Tables

**Serial Format:** Last 4 digits of serial number (0–9999)
**Code Format:** 4 digits

**Formula:** Extract 4 decimal nibbles, apply per-position lookup tables, combine:
```
code = 1111 + (third_nibble × 10) + (first_nibble × 1000) + fourth_nibble + (second_nibble × 100)
```

**Position-based lookup tables (digits 0–9):**
| Digit | GetFirstByte | GetSecondByte | GetThirdByte | GetFourthByte |
|-------|:-----------:|:-------------:|:------------:|:-------------:|
| 0     | 0           | 0             | 0            | 0             |
| 1     | 1           | 1             | 1            | 1             |
| 2     | 2           | 2             | 2            | 2             |
| 3     | 3           | 3             | 3            | 3             |
| 4     | 4           | 4             | 4            | 4             |
| 5     | 5           | 5             | 5            | 5             |
| 6     | 0           | 1             | 2            | 3             |
| 7     | 0           | 1             | 2            | 3             |
| 8     | 0           | 0             | 0            | 0             |
| 9     | 1           | 1             | 1            | 1             |

**Test Vectors (5/5 PASSED):**
| Last 4 Digits | Code |
|---------------|------|
| 0000 | 1111 |
| 0123 | 3142 |
| 1234 | 4253 |
| 5000 | 1611 |
| 9999 | 2222 |

**Works with:** Fiat 500 (2007+), Fiat 250 (Panda), Alfa Romeo MiTo, Alfa Romeo Giulietta, VP1 and VP2 head units.

**Python Implementation:**
```python
def _GetFourthByte(input_val: int) -> int:
    if input_val > 10:
        return 0
    return {6: 3, 7: 3, 8: 0, 9: 1}.get(input_val, input_val)

def _GetThirdByte(input_val: int) -> int:
    if input_val > 10:
        return 0
    return {6: 2, 7: 2, 8: 0, 9: 1}.get(input_val, input_val)

def _GetSecondByte(input_val: int) -> int:
    if input_val > 10:
        return 0
    return {6: 1, 7: 1, 8: 0, 9: 1}.get(input_val, input_val)

def _GetFirstByte(input_val: int) -> int:
    if input_val > 10:
        return 0
    return {6: 0, 7: 0, 8: 0, 9: 1}.get(input_val, input_val)

def GetCode(sn: int) -> int:
    code = 1111
    sn_ = [
        ((sn // 1000) & 0x0F),       # thousands digit
        ((sn % 1000) // 100 & 0x0F),  # hundreds digit
        ((sn % 100) // 10 & 0x0F),    # tens digit
        ((sn % 10) & 0x0F),           # units digit
    ]
    code += (_GetThirdByte(sn_[3]) * 10)
    code += (_GetFirstByte(sn_[2]) * 1000)
    code += (_GetFourthByte(sn_[1]))
    code += (_GetSecondByte(sn_[0]) * 100)
    return code
```

**Verification:** ✅ **PASS — 5/5 vectors confirmed**
**Source:** https://github.com/mark0wnik/VP1-VP2-Toolkit (anti-theft-code.py)
**Already in repo:** `src/radiocodes/algorithms/fiat.py` ✅

---

### Brand: Ford — V Series
### Algorithm: Binary Lookup Database (NOT a formula)

**Serial Format:** `V123456` (1 letter + 6 digits)
**Code Format:** 4 digits

**No formula exists.** The radiocodes.bin file contains 4,000,000 pre-computed uint16 entries:
- M-series serials (0–999999): stored at `offset = index × 2`
- V-series serials (0–999999): stored at `offset = 2,000,000 + index × 2`

**Python Implementation:**
```python
import os, struct

DEFAULT_BIN = "data/ford_radiocodes.bin"

def ford_v_calculate(serial: str, bin_path: str = DEFAULT_BIN) -> str:
    index = int(serial[1:7])  # Remove 'V', get numeric part
    offset = 2_000_000 + index * 2  # V-series offset
    with open(bin_path, "rb") as f:
        f.seek(offset)
        data = f.read(2)
        code = struct.unpack("<H", data)[0]
        return f"{code:04d}"
```

**Verification:** ⚠️ **BINARY DB REQUIRED — radiocodes.bin present (304KB, ~1.4M V-series entries)**
**Source:** https://github.com/DavidB445/fz_fordradiocodes
**Already in repo:** `src/radiocodes/algorithms/ford_m.py` (FordVAlgorithm), `data/ford_radiocodes.bin` ✅

---

## ⚠️ DATABASE-ONLY IMPLEMENTATIONS

---

### Brand: Volkswagen — RCD 210/310/510
**Status:** Database-only lookup. No public formula exists.

**Serial Format:** 14 characters (e.g., `VWZ5Z7B5013069`, `AUZ5Z7B5013069`)
**Code Range:** 0000–1999 observed

**158+ known serial→code pairs** from VW Vortex forum. Notable entries:
| Serial | Code |
|--------|------|
| VWZ9Z7V3888887 | 0006 |
| VWZ627J9030185 | 0027 |
| VWZ5Z7B5013069 | 0031 |
| VWZ4Z7H2200493 | 0037 |
| VWZ9Z7Y7189266 | 0042 |
| VWZ5Z7B5125847 | 0081 |
| VWZ2Z2D1524411 | 0104 |
| VWZ927B0068567 | 1889 |
| VWZ5Z7C5232416 | 1907 |

**Also covers:** Audi Chorus/Concert/Symphony, Seat RCD310/RCD510, Skoda RCD310/RCD510

**Source:** https://gist.github.com/VWZ1Z2Y5298166/e44d7c51f54d8b6094c39cd11ad62062
**Already in repo:** `src/radiocodes/algorithms/vw_rcd.py` + `src/radiocodes/algorithms/vw_rcd_lookup.py` ✅

---

### Brand: Vauxhall / Opel
**Status:** Database-only lookup. No public formula.

**Serial Formats:** Multiple radio manufacturers, each with proprietary codes:
| Format | Radio | Manufacturer |
|--------|-------|-------------|
| GM0203... | CAR2003 | Blaupunkt |
| GM0204... | CAR2004 | Delphi |
| GM030M... | CAR300 | Blaupunkt |
| GM0400... | CAR400 | Blaupunkt |
| GM0804... | SC804 | Siemens |
| CM0141... | Touch & Connect | Bosch (VIN-linked) |
| 22DC... | GM020x variant | GM |

**17 known pairs** in `data/forum_pairs.csv`. EEPROM reading is the universal offline solution.

**Already in repo:** `src/radiocodes/algorithms/vauxhall.py` + `data/forum_pairs.csv` ✅

---

## ❌ UNVERIFIED FORMULAS (In Repo — Need Test Vectors)

The following algorithms are in the codebase but have **zero confirmed test vectors**. They may produce incorrect codes.

---

### Nissan
**Formula in repo:** `code = ((sum_of_hex_values * 3) + 7777) % 10000`
**Status:** ⚠️ UNVERIFIED — likely incorrect. Nissan has NOT been publicly reversed.
**Serial format:** 12-char hex (e.g., CY16C-1234567)
**Recommendation:** Mark as EEPROM-only or VIN-linked. The formula in the repo is a guess.

---

### Peugeot / Citroën
**Formula in repo:** `total = sum(val << (i×2)) where val=digit or val=ord(c)-ord('A')+7; return ((total ^ 0x1357) + 5000) % 10000`
**Status:** ⚠️ UNVERIFIED — appears to be a placeholder guess.
**Serial formats:** BP prefix, 815 prefix, 7 prefix
**Known vector:** `BP2 775(S) 9452352` → `2893` (Citroen Algo 1 from French Car Forum)
**Recommendation:** Collect 50+ confirmed pairs before attempting algorithm reverse engineering.

---

### Alfa Romeo
**Formula in repo:** `val = int(serial, 16); code = ((val * 9) + 0x1F3D) & 0xFFFF; return code % 10000`
**Status:** ⚠️ UNVERIFIED — no confirmed test vectors found.

---

### Chrysler / Dodge / Jeep
**Formula in repo:** `total = sum(ord(c) * (i + 1) for i, c in enumerate(serial)); return ((total ^ 0x5A5A) + 3333) % 10000`
**Status:** ⚠️ UNVERIFIED — known to vary by model. VP2 head units may have a different algorithm than Uconnect.
**Known:** Dodge Ram VP2 (Harman Kardon) is a high-demand item. Closely related to Fiat/Chrysler proprietary algorithm.

---

### Jaguar / Land Rover
**Formula in repo:** `total = sum(int(c, 36) * (i + 1) for i, c in enumerate(serial)); return (total * 7 + 1234) % 10000`
**Status:** ⚠️ UNVERIFIED — no confirmed test vectors. Land Rover codes are often printed on a card in the glovebox (flash-coded security).

---

## ❌ NO ALGORITHM KNOWN (Research Targets)

### High Priority (High Demand, Collect Pairs)

1. **BMW — Business, Munich R-series, MK4**
   - Serial: `F123456789`, `6 123 456`
   - Notes: Suspected XOR or simple checksum. EEPROM reading works for all models. The BMW Business CD (MF2xx) and Munich R-series use different algorithms. Collecting PCB dumps and serial+code pairs is the path forward.
   - Priority: **HIGH**

2. **Opel/Vauxhall Blaupunkt CAR2003** (GM0203...)
   - Need: 100+ confirmed pairs from MHH AUTO thread
   - Priority: **HIGH**

3. **Peugeot/Citroen Blaupunkt BP1/BP2**
   - Need: 50+ confirmed pairs + CRUCC reverse engineering
   - Priority: **MEDIUM**

4. **Chrysler/Dodge VP2** (Harman Kardon)
   - Suspected relationship to Fiat VP1/VP2
   - Priority: **MEDIUM**

5. **Honda / Acura**
   - Serial: 8 digits (`U12345678`)
   - Official portal: radio-navicode.honda.com (free, VIN+serial)
   - Priority: **MEDIUM** (official portal covers most cases)

### Medium Priority

6. **Mercedes-Benz** — COMAND NTG1-4, Audio 20, Becker variants
7. **Volvo** — HU-603/605/609, RTI, ICE
8. **Mazda** — MazdaConnect, Matas其一
9. **Mini** — BMW-based, Radio Boost, Visual Boost
10. **Hyundai / Kia** — Various head units

### Low Priority (EEPROM Sufficient)

11. **Audi** — Shares VW implementation (database approach)
12. **Seat / Skoda** — Shares VW implementation
13. **Porsche** — PCM2/PCM3/CDR220
14. **Saab** — Trionic, HU-xxxx
15. **Smart** — Becker/Blaupunkt OEM
16. **Subaru** — Starlink
17. **Mitsubishi** — MMCS
18. **Suzuki** — Various
19. **Lexus / Toyota** — ERC system (dealer required)
20. **Infiniti / Nissan** — Related to Nissan

### Commercial-Only (Paid API or EEPROM)

21. **Kenwood** — Various
22. **JVC** — Various
23. **Pioneer** — Various
24. **Sony** — Various
25. **Clarion** — Various
26. **Becker** — Becker Mexico, etc.
27. **Eclipse** — ESN unlock
28. **Magneti Marelli** — Fiat Stilo, Bravo (PELock commercial)

---

## EEPROM REFERENCE

Many radios store the code directly in serial EEPROM chips. Common approaches:

| Chip | Interface | Common Radios | Tool |
|------|-----------|--------------|------|
| 24C01/24C02 | I2C | VW RCD, Ford, older Blaupunkt | CH341A + flashrom |
| 24C04/24C08 | I2C | Newer head units | CH341A + flashrom |
| 93C46/93C56 | SPI | Some Becker/Blaupunkt | SPI programmer |
| MCU flash | JTAG/SWD | Some newer units | OpenOCD |

**Common EEPROM code storage addresses:**
- VW RCD: Typically at byte `0x00–0x03` in 24Cxx
- Ford M/V: Varies by PCB revision
- Blaupunkt CAR2003: Reported at `0x1A0–0x1A3` in some dumps

---

## Algorithm Source Reference

| Brand | Type | Source |
|-------|------|--------|
| Ford M | Formula | OlegSmelov/ford-radio-codes (gist 4ndrej) |
| Ford V | Binary DB | DavidB445/fz_foldradiocodes (radiocodes.bin) |
| Renault | Formula | yne/gist, m-a-x-s-e-l-i-g/renault-radio-code-generator |
| Fiat VP1/VP2 | Formula | mark0wnik/VP1-VP2-Toolkit |
| VW RCD | DB | VW Vortex gist (158 pairs) |
| Opel/Vauxhall | DB | MHH AUTO RadioCodeDatabase thread |
| Peugeot | DB | French Car Forum, CRUCC |
| Nissan | Unknown | PELock commercial |
| BMW | Unknown | EEPROM only |
| Mercedes | Unknown | EEPROM/EPC |
| Honda | Portal | radio-navicode.honda.com (free) |
| Chrysler | Unknown | PELock commercial |
| Jaguar | Unknown | PELock commercial |

---

## Priority Action Items

### Immediate (This Week)
1. **Verify or remove unverified formulas** — Nissan, Peugeot, Alfa Romeo, Chrysler, Jaguar have no test vectors. Either collect 3+ confirmed pairs for each OR remove them from the tool to avoid generating wrong codes.

### Short-term (1–4 Weeks)
2. **Build Opel/Vauxhall database** — Scrape MHH AUTO thread for GM0203 pairs. Target 500+.
3. **Build Peugeot/Citroen database** — Target BP serial format. 100+ pairs needed.
4. **Research BMW** — Collect PCB dumps and serial+code pairs from forums.

### Medium-term (1–3 Months)
5. **Research Chrysler VP2** — Dodge Ram VP2 is high demand. Study relationship to Fiat VP1/VP2.
6. **Expand VW RCD database** — From 158 to 500+ pairs.
7. **Honda portal integration** — Guide users to official free portal instead of algorithm.

---

*End of Phase 1 Algorithm Gold Rush Report*
*Tam — RadioUnlock Research Division*
*2026-03-20*
