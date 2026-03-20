# 📻 RadioUnlock

**Free, offline car radio unlock code calculator for Windows.**

End the racket of paying £5-20 for a radio code that's been sitting behind a paywall since 1995.

---

## ⬇️ Download

**[Download RadioUnlock-Windows.exe](https://github.com/YOUR_GITHUB/radio-codes/releases)** ← set up GitHub Pages to host

> No installation needed. No admin required. Runs offline.

---

## ✅ What's Working (Free & Offline)

| Brand | Radio Types | Status | How |
|-------|------------|--------|-----|
| **Ford M Series** | 4500, 4600, 5000, 6000 RDS EON | ✅ Working | Algorithm: 10x10 lookup table |
| **Ford V Series** | V123456 serial format | ✅ Working | Requires `ford_radiocodes.bin` (included) |
| **Renault / Dacia** | All models, pre-code format | ✅ Working | Algorithm: confirmed formula |
| **VW RCD** | RCD210, RCD310, RCD510, Chorus, Concert, Symphony | ⚠️ Lookup | 156 known serials in database |

## ⚠️ Not Reversible (yet)

These brands have **no free algorithm** — the codes are stored in the radio's EEPROM or use proprietary encryption:

| Brand | Options |
|-------|---------|
| **Vauxhall / Opel** | EEPROM read (CH341A + 24Cxx) |
| **Peugeot / Citroën** | Multiple algos, EEPROM read |
| **Fiat / Alfa** | VP1/VP2 toolkit exists, EEPROM read |
| **Nissan** | VIN-linked service only |
| **Honda** | VIN-linked service only |
| **Toyota** | ERC proprietary, dealer only |
| **Jaguar / Land Rover** | EEPROM read |
| **Chrysler / Dodge / Jeep** | Uconnect — EEPROM read |

---

## 🔧 EEPROM Reading (for unsupported brands)

If your serial isn't in the database, you'll need to read the radio's EEPROM:

1. **Remove the radio** from the car
2. **Identify the chip** — usually a 24C01, 24C02, 24C04, or 24C08 (8-pin SOIC)
3. **Solder** it to a **CH341A programmer** (~£5 on eBay)
4. **Read the chip** with `flashrom` or the CH341A software
5. **Find the code** — it's stored in plain text at a known address per radio model

---

## 📻 How to Find Your Serial

### Ford M / V Series
1. Hold **preset buttons 1 AND 6** together
2. While holding, turn the radio on
3. Display shows serial (e.g. **M123456** or **V123456**)

### Renault / Dacia
1. Hold **buttons 1 AND 6** together
2. Press **POWER**
3. Display shows **PRE-CODE X123** (e.g. D123)

### VW RCD (Chorus / Concert / Symphony)
1. Turn radio on — shows **SAFE**
2. Hold **FM2 + SCAN** buttons together
3. Serial appears (14 characters, starts **VWZ** or **AUZ**)

---

## 🖥️ Running from Source

```bash
pip install PySide6
python src/radiocodes/main.py
```

---

## 🔨 Building

```bash
pip install PySide6 PyInstaller
pyinstaller --windowed --onefile src/radiocodes/main.py
# Output: dist/RadioUnlock
```

---

## 📋 Requirements

- **Windows 10/11 x64**
- No admin required (runs in user space)
- No internet required (fully offline)
- ~300MB disk space

---

## ⚠️ Disclaimer

This tool is for personal use when you've lost your radio code. Always check vehicle documents first. We are not responsible for damaged radios or vehicles.
