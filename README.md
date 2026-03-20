# 📻 RadioUnlock — Free Car Radio Code Calculator

> **Radio codes have been paywalled for 30 years. Not anymore.**

A free, open-source car radio code calculator that actually works. No ads, no accounts, no fees.

🌐 **Live Web App:** https://killahbtc.github.io/radio-codes/

📥 **Windows App:** Download from [Releases](https://github.com/killahbtc/radio-codes/releases)

---

## What It Does

Enter your radio's serial number → get the unlock code instantly.

## Features

- ✅ **Verified algorithms** — Ford M/V, Renault, Fiat VP1/VP2
- ✅ **431 verified codes** across 41 brands in the lookup database
- ✅ **EEPROM Reader** — extract code from radio's memory chip
- ✅ **Free portal links** — Honda, Nissan official free portals
- ✅ **Honest accuracy** — we tell you which codes are verified vs unverified
- ✅ **100% free forever** — no ads, no in-app purchases
- ✅ **Works on any phone** — web app, no install needed

## Coverage

| Status | Brands |
|--------|--------|
| ✅ Verified algorithms | Ford, Renault/Dacia, Fiat VP1/VP2, VW RCD, Vauxhall/Opel |
| ⚠️ Unverified (use EEPROM) | Nissan, Peugeot, Alfa Romeo, Chrysler, Jaguar/Land Rover |
| 🌐 Free official portal | Honda (radio-navicode.honda.com) |
| 🔜 Coming soon | Toyota/Lexus, BMW, Mercedes, Volvo |

## Quick Start — Windows

1. Download the latest `RadioUnlock.exe` from [Releases](https://github.com/killahbtc/radio-codes/releases)
2. Run it — no install needed
3. Select your car brand
4. Enter your radio serial number
5. Get your code

## Quick Start — Web (Any Phone)

1. Open https://killahbtc.github.io/radio-codes/
2. Select your car brand
3. Enter your radio serial number
4. Get your code

## Quick Start — EEPROM Reader

For brands without algorithms, or if the calculator doesn't find your code:

1. Remove the radio from your car
2. Locate the 8-pin SOIC EEPROM chip (24C01–24C64)
3. Read it with a **CH341A USB programmer** (~£5 on eBay)
4. Load the `.bin` dump in RadioUnlock
5. Full chip scan finds the code automatically

Supported EEPROM chips: 24C01, 24C02, 24C04, 24C08, 24C16, 64

## Brand Status Guide

- **✅ Green (Working)** — Algorithm verified with test vectors. These work perfectly.
- **⚠️ Yellow (Unverified)** — No confirmed algorithm yet. Use EEPROM reader for guaranteed results.
- **🌐 Portal (Official Free)** — Brand has a free official portal. Link provided in app.
- **🔜 Grey (Coming Soon)** — Research ongoing.

## How to Find Your Radio Serial

### Ford
- **M-Series:** Hold buttons `1` and `6` while turning on the radio
- **V-Series:** Hold buttons `1` and `6` while turning on
- Look for serial starting with `M` or `V` followed by 6 digits

### Renault
- Turn on radio — display shows `PRE-CODE XXXX`
- That's your 4-character precode (letter + 3 digits)

### Vauxhall/Opel
- Enter wrong code 3 times — serial displays automatically
- Or remove radio and check label

### Fiat/Alfa Romeo
- Remove radio, check label on top or side
- Serial is usually 4 digits

## Development

```bash
# Clone
git clone https://github.com/killahbtc/radio-codes
cd radio-codes

# Run desktop app
cd app && flet run

# Build web app
cd app && flet build web

# Run tests
python3 -m pytest
```

## Algorithm Sources

| Brand | Algorithm | Source |
|-------|-----------|--------|
| Ford M | 10×10 lookup table | github.com/OlegSmelov/ford-radio-codes |
| Ford V | Binary database | radiocodes.bin (4M entries) |
| Renault | Precode modular arithmetic | github.com/ojacquemart/renault-radio-code-list |
| Fiat VP1/VP2 | Nibble-extract lookup | github.com/mark0wnik/VP1-VP2-Toolkit |
| VW RCD | Lookup database | 158+ public pairs |
| Vauxhall/Opel | Lookup + EEPROM | 17+ public pairs |

## Contributing

Found a serial+code pair? Submit it via GitHub Issues or PR. Every verified pair makes the tool better for everyone.

## Disclaimer

RadioUnlock is provided free for legitimate use. Radio codes exist to prevent theft — this tool is for recovering your own radio after a battery change or power loss. Use responsibly.
