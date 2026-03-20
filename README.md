# 📻 RadioUnlock — Free Car Radio Code Calculator

> *Radio codes have been paywalled for 30 years. Not anymore.*

**RadioUnlock** is a completely free, no-ads, open-source tool that calculates car radio unlock codes. Works on Windows, Mac, Linux, Android, iOS, and in any browser.

---

## ✅ What's Working

### Algorithms (instant, no internet needed)
| Brand | Serial Format | Status |
|-------|--------------|--------|
| **Ford M-Series** | `M123456` | ✅ Verified |
| **Ford V-Series** | `V123456` | ✅ Verified |
| **Renault / Dacia** | `D123` | ✅ Verified |
| **Fiat / Alfa Romeo** | `VP1-xxxx`, `VP2-xxxx` | ✅ Verified |
| **VW RCD** | Full 17-char serial | ✅ Lookup |
| **Vauxhall / Opel** | `GM0203...` | ✅ Lookup |
| **Peugeot / Citroën** | `BPxxxx...` | ✅ Lookup |
| **Nissan** | `BPxxxx...` | ✅ Lookup |

### Free Lookup Database
**431 verified code pairs across 41 brands** scraped from public forums:

`renault(107) · kia(52) · ford(50) · opel(19) · hyundai(13) · blaupunkt(13) · fiat(12) · landrover(12) · rover(12) · nissan(11) · mini(11) · audi(10) · vw(9) · mercedes(9) · peugeot(8) · and 27 more...`

### EEPROM Reader
Reads the radio's EEPROM chip directly to extract the code — works for **any locked radio** regardless of brand.

**Supported chips:** 24C01 · 24C02 · 24C04 · 24C08 · 24C16 · 24C64

**Supported radios:** Blaupunkt CAR2003/2004/300/CD300 · Siemens VDO CR500 · Ford 6000CD · Bosch Touch & Connect · Renault · VW RCD · Nissan Connect · + Generic full-chip BCD scan

---

## 💾 EEPROM How-To

1. Remove radio from dashboard
2. Find the 8-pin SOIC chip (marked `24Cxx`) on the circuit board
3. Solder it to a **CH341A programmer** (~£5 on eBay)
4. Read the chip with [flashrom](https://flashrom.org) or the CH341A software → save as `.bin`
5. Open the `.bin` in RadioUnlock → full chip scan finds the code

---

## 📱 Download

### Windows Desktop App
Download the installer here:
```
releases/
```

### Android / iOS / Web App
Built with [Flet](https://flet.dev). Run from source:

```bash
# Install Flet
pip install flet

# Run as web app (opens in browser)
cd app
flet run --web

# Run as desktop app
flet run

# Build Android APK
flet pack --android app/main.py

# Build Windows .exe
flet pack --windows app/main.py
```

---

## 🖥️ Windows Desktop App (PySide6)

For the full-featured Windows app with EEPROM reader built-in:

```bash
pip install -r requirements.txt
python src/radiocodes/gui/main.py
```

Or download the pre-built `RadioUnlock.exe` from releases.

---

## 🔧 Build from Source

```bash
git clone https://github.com/killahbt/radio-codes.git
cd radio-codes

# Desktop app dependencies
pip install -r requirements.txt
python src/radiocodes/gui/main.py

# Mobile app dependencies
pip install flet
cd app && flet run --web
```

---

## 🌐 API (free, no key needed)

Want to build your own tool? The lookup engine works as a Python module:

```python
from radiocodes.lookup_engine import load_csv, get_stats, lookup

load_csv()

# Get all stats
stats = get_stats()
print(f"{stats['total_pairs']} codes across {len(stats['brands'])} brands")

# Lookup by serial
result = lookup("M025345", "ford")
print(result)  # {'code': '3306', 'model': '6000CD', 'source': 'forum'}

# Lookup by prefix (for partial serials)
result = lookup("GM0203", "opel")
print(result)  # {'code': '2411', 'model': 'CAR2003', 'source': 'forum'}
```

---

## 🛠️ Supported Brands

acura · alfa romeo · audi · blaupunkt · bmw · cadillac · chery · chrysler · citroen · dacia · daewoo · fiat · ford · honda · hyundai · jeep · kia · lancia · land rover · lexus · maserati · mazda · mercedes · mini · mitsubishi · nissan · opel · peugeot · pontiac · renault · rover · seat · skoda · smart · subaru · suzuki · toyota · vauxhall · volkswagen · volvo · vw

---

## 📊 Stats

| Metric | Value |
|--------|-------|
| Verified code pairs | 431 |
| Brands covered | 41 |
| Working algorithms | 8 |
| EEPROM profiles | 12 |
| License | Free forever |

---

## 🤝 Support

This is a community project. If it helped you:
- Share it with someone who needs it
- Post on car forums / Reddit / Facebook groups
- Report missing codes so we can add them

Found a working serial+code pair? Open an issue or PR — every addition helps.

---

*RadioUnlock — Free forever. No ads. No paywalls. No catch.*
