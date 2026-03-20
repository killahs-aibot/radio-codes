# COMPLETE BRAND COVERAGE ANALYSIS
# RadioUnlock — What's Working, What's Not, What's Needed

## VERIFIED WORKING ALGORITHMS ✅

| Brand | Algorithm Type | Implementation | Test Vectors |
|-------|---------------|----------------|--------------|
| **Ford M Series** | 10×10 Lookup Table | `ford_m.py` | 5/5 ✅ |
| **Ford V Series** | Binary DB (radiocodes.bin) | `ford_m.py` FordVAlgorithm | Binary ✅ |
| **Renault/Dacia** | Precode Math Formula | `renault.py` | 13/13 ✅ |
| **Fiat VP1/VP2** | Nibble Extract + Lookup | `fiat.py` | 5/5 ✅ |

## PARTIAL/WORKING WITH DATABASE ⚠️

| Brand | Approach | Coverage | Status |
|-------|----------|----------|--------|
| **VW/Audi/Seat/Skoda** | Forum DB lookup | 158 pairs | Needs more pairs |
| **Vauxhall/Opel** | Forum DB lookup | 17 pairs | Needs more pairs |

## PORTAL-ONLY (Free, Official) 🌐

| Brand | Portal URL | Notes |
|-------|-----------|-------|
| **Honda** | https://radio-navicode.honda.com/ | Free, VIN+serial |
| **Acura** | https://radio-navicode.acura.com/ | Free, VIN+serial |
| **Nissan** | https://radio-navicode.nissan.com/ | Free, VIN+serial |

## DEALER/EEPROM ONLY 🔒

| Brand | Options | Notes |
|-------|---------|-------|
| **Toyota/Lexus** | Dealer or EEPROM | ERC system, 16-char ERC |
| **BMW** | EEPROM only | No algorithm known |
| **Mercedes** | EEPROM only | COMAND NTG1-4 |
| **Volvo** | EEPROM only | HU-603/605/609 |
| **Mazda** | EEPROM only | MazdaConnect |
| **Mini** | EEPROM only | BMW-based |
| **Hyundai/Kia** | EEPROM only | Various |
| **Mitsubishi** | EEPROM only | MMCS |
| **Suzuki** | EEPROM only | Various |

## UNVERIFIED/PLACEHOLDER ❌

| Brand | Current Status | Recommendation |
|-------|---------------|----------------|
| **Nissan** | Formula is a guess | Use official portal |
| **Peugeot/Citroën** | No confirmed formula | Database approach |
| **Alfa Romeo** | No formula | Try Fiat VP1/VP2 for BP serials |
| **Chrysler/Dodge/Jeep** | No formula | Try VP2 last-4 approach |
| **Jaguar/Land Rover** | No formula | EEPROM or security card |

---

## ALTERNATE RENAULT IMPLEMENTATION

Found alternate JavaScript implementation that passes all test vectors:

```javascript
function renault(a, b, c, d) { // 'A', 1, 0, 0
    left = (a.charCodeAt(0) - 65) * 10 + b;
    right = ((left + c * 10 + d) * 7) % 100;
    return String((259 % Math.abs(left)) % 100).padStart(2, 0) + (right % 10) + (right / 10 | 0);
}
```

Python equivalent:
```python
def renault_alt(precode):
    a, b, c, d = precode[0], int(precode[1]), int(precode[2]), int(precode[3])
    left = (ord(a) - 65) * 10 + b
    right = ((left + c * 10 + d) * 7) % 100
    left_mod = (259 % abs(left)) % 100
    return str(left_mod).zfill(2) + str(right % 10) + str(right // 10)
```

---

## KEY FINDINGS

1. **Only 3 openly verified algorithms exist**: Ford M, Renault, Fiat VP1/VP2
2. **Ford V uses a binary database** — not a real-time formula
3. **VW and Opel** need more forum pair collection to improve coverage
4. **Most brands** have NO public algorithm — EEPROM is the universal solution
5. **PELock commercial SDK** covers 15+ brands — they are the de facto standard
6. **Honda, Nissan, Acura** have free official portals — direct users there

---

## PRIORITY ACTION ITEMS

### HIGH PRIORITY
1. Remove unverified formulas (Nissan, Peugeot, Chrysler, Jaguar) or mark strongly as UNVERIFIED
2. Expand VW database (158 → 500+ pairs) via forum scraping
3. Expand Opel database (17 → 500+ pairs) via MHH AUTO scraping
4. Research Blaupunkt BP algorithm — could unlock multiple brands

### MEDIUM PRIORITY
5. Research Chrysler VP2 (Dodge Ram Harman Kardon) — high demand
6. Research BMW — collect serial+code pairs from forums
7. Ford TravelPilot research (EX, FX, NX)

### LOW PRIORITY
8. Volvo, Mazda, Mercedes — EEPROM sufficient
9. Hyundai/Kia, Mitsubishi, Suzuki — low demand

---

## FORUM SOURCES FOR DATABASE BUILDING

- **VW**: vwvortex.com, forum.ross-tech.com
- **Opel/Vauxhall**: mhhauto.com (Robot's Forum), vxcc.com
- **Peugeot/Citroën**: frenchcarforum.co.uk, peugeotforums.com
- **BMW**: mhhauto.com, bimmerforums.com
- **Ford**: fordforums.com, ford-v-series lookup

## EEPROM REFERENCE

| Chip | Interface | Common Radios | Address |
|------|-----------|--------------|---------|
| 24C01 | I2C | Older units | 0x00-0x03 |
| 24C02 | I2C | VW RCD, Ford | 0x00-0x03 |
| 24C04 | I2C | Newer units | varies |
| 93C46 | SPI | Some Blaupunkt | varies |
| MCU Flash | JTAG | Newer units | full dump |

**Tool**: CH341A programmer + flashrom
**Software**: https://flashrom.org/

---

## COMPLETE SOURCE REFERENCE

### Open Source Repositories
1. `github.com/OlegSmelov/ford-radio-codes` — Ford M algorithm
2. `github.com/DavidB445/fz_fordradiocodes` — Ford V database
3. `github.com/mark0wnik/VP1-VP2-Toolkit` — Fiat VP1/VP2
4. `gist.github.com/yne/d6dad90416727c2e027774857233524f` — Renault gist
5. `github.com/m-a-x-s-e-l-i-g/renault-radio-code-generator` — Renault JS
6. `github.com/ojacquemart/renault-radio-code-list` — 23K test vectors
7. `gist.github.com/VWZ1Z2Y5298166/e44d7c51f54d8b6094c39cd11ad62062` — VW pairs
8. `github.com/killahbtc/radio-codes` — This project ⭐

### Commercial (Paid API)
- `pelock.com/products/radio-code-calculator` — PELock SDK (15+ brands)

### Official Portals (Free)
- `radio-navicode.honda.com` — Honda (US)
- `radio-navicode.acura.com` — Acura (US)
- `radio-navicode.nissan.com` — Nissan (US)

---

*Last Updated: 2026-03-20*
*Part of RadioUnlock project*
