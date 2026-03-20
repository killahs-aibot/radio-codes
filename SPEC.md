# RadioUnlock — Free Car Radio Code Calculator

**Free, offline car radio unlock code calculator for Windows.**

End the racket of paying £5-20 for a radio code that's been sitting behind a paywall since 1995.
Built for mechanics, car flippers, and anyone who's bought a car with a locked stereo.

---

## What It Does

Enter your radio's serial number → get the unlock code instantly → free.

No internet required. No API calls. No paywalls.

---

## Supported Brands

| Brand | Radio Types | Serial Format | Code Output |
|-------|------------|---------------|-------------|
| Ford | M Series, V Series, TravelPilot | 6-7 digits | 3-4 digits |
| Renault / Dacia | All models | 1 letter + 3 digits | 4 digits |
| VW / Audi / Seat / Skoda | RCD, Chorus, Concert, Symphony | 14-char | 4 digits |
| Vauxhall / Opel | CDX, CDC, Navi | 4-6 chars | 4 digits |
| Peugeot / Citroen | RT3, RT4, RNEG, MyWay | 4-6 chars | 4 digits |
| Fiat | Uconnect, Blue&Me, 500 | 4-6 chars | 4 digits |
| Nissan | Connect, Patrol, Qashqai | 12-char | 4-5 digits |
| Honda | Civic, Accord, CR-V | 5-10 chars | 5 digits |
| Toyota | ERC, Touch, Entune | 16-char | 5 digits |
| Alfa Romeo | Connect, Nav+ | Serial | 4 digits |
| Chrysler / Dodge / Jeep | Uconnect | 4-6 chars | 4 digits |
| Jaguar / Land Rover | InControl, Touch Pro | 5-8 chars | 4 digits |
| Mitsubishi |  | Serial | 4 digits |
| Hyundai / Kia |  | Serial | 4 digits |

---

## GUI Design

### Color Scheme
- **Background:** #0D1117 (near-black)
- **Surface:** #161B22 (dark card)
- **Accent:** #58A6FF (blue, like a radio display)
- **Success:** #3FB950 (green LED)
- **Warning:** #D29922 (amber LED)
- **Error:** #F85149 (red)
- **Text:** #E6EDF3 (off-white)
- **Muted:** #7D8590 (dim)

### Layout
Single window, no tabs. Everything on one screen.

```
┌─────────────────────────────────────────────────────────┐
│  📻 RadioUnlock                          [Settings ⚙️]   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   SELECT BRAND                                           │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│   │   Ford   │ │ Renault  │ │   VW     │ │Vauxhall  │  │
│   │   🟢     │ │   🟢     │ │   🟢     │ │   🟢     │  │
│   └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│   │ Peugeot  │ │   Fiat   │ │  Nissan  │ │  Honda   │  │
│   │   🟢     │ │   🟢     │ │   🟢     │ │   🟢     │  │
│   └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                         │
│   ─────────────────────────────────────────────────     │
│                                                         │
│   RADIO MODEL                                           │
│   [Ford M Series ──────────────────▼]                   │
│                                                         │
│   SERIAL NUMBER                                         │
│   ┌─────────────────────────────────────────────────┐   │
│   │  123456                                         │   │
│   └─────────────────────────────────────────────────┘   │
│   Format hint: 6 digits found on label or screen        │
│                                                         │
│   ┌─────────────────────────────────────────────────┐   │
│   │              🔓 CALCULATE CODE                   │   │
│   └─────────────────────────────────────────────────┘   │
│                                                         │
│   ─────────────────────────────────────────────────     │
│                                                         │
│   YOUR CODE                                             │
│   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                 │
│   │  5   │ │  2   │ │  7   │ │  3   │                 │
│   └──────┘ └──────┘ └──────┘ └──────┘                 │
│           ↑ enter this into your radio                 │
│                                                         │
│   Status: ✓ Code calculated for Ford M Series           │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  How to find your serial →  [Help ▼]                   │
└─────────────────────────────────────────────────────────┘
```

### Brand Selector
- Grid of large square buttons (80x80px), 4 per row
- Each button shows brand name + radio icon
- Selected state: blue border glow
- "How to find serial" button at bottom → expands inline help per brand
- Green dot = algorithm implemented, working
- Grey dot = coming soon

### Code Display
- Large individual digit boxes (like an LED display)
- Each digit is a separate QLabel in a styled box
- 4-6 boxes depending on code length
- "Copy to clipboard" button below
- Success animation: brief green pulse on the digit boxes

### Settings (gear icon)
- Language: English (default), expandable
- Theme: Dark (default) / Light
- Always on top: checkbox
- Check for updates: button

### Help Panel
- Expandable section below the form
- Per-brand instructions for finding the serial number
- Three ways: label on radio, screen display, disconnect method

---

## Technical Architecture

```
radio-codes/
├── src/
│   ├── radiocodes/
│   │   ├── __init__.py
│   │   ├── main.py              # Entry point
│   │   ├── gui/
│   │   │   ├── __init__.py
│   │   │   ├── main_window.py   # Main window (PySide6)
│   │   │   ├── brand_selector.py # Brand grid widget
│   │   │   ├── code_display.py   # LED digit display
│   │   │   ├── serial_input.py   # Input field with validation
│   │   │   ├── help_panel.py     # How to find serial
│   │   │   └── styles.py         # Dark theme stylesheet
│   │   ├── algorithms/
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # Base class + interface
│   │   │   ├── ford_m.py         # Ford M Series
│   │   │   ├── ford_v.py         # Ford V Series
│   │   │   ├── renault.py        # Renault/Dacia
│   │   │   ├── vw.py             # VW RCD
│   │   │   ├── vauxhall.py       # Vauxhall/Opel
│   │   │   ├── peugeot.py        # Peugeot/Citroen
│   │   │   ├── fiat.py           # Fiat
│   │   │   ├── nissan.py         # Nissan
│   │   │   ├── honda.py          # Honda
│   │   │   └── toyota.py         # Toyota ERC
│   │   └── brands/
│   │       ├── __init__.py
│   │       └── registry.py       # Brand → Algorithm mapping
│   └── radiocodes.iss            # Inno Setup installer script
├── build/                         # PyInstaller temp files
├── dist/                          # Built executables
├── SPEC.md                        # This file
└── README.md                      # User-facing readme
```

---

## Algorithm Interface

Every brand algorithm inherits from `BaseRadioAlgorithm`:

```python
class BaseRadioAlgorithm:
    brand_name: str
    supported_models: List[str]
    code_length: int  # e.g. 4 for 4-digit codes

    def validate_serial(self, serial: str) -> bool:
        """Check serial format before calculating."""
        raise NotImplementedError

    def calculate(self, serial: str) -> str:
        """Calculate the unlock code from serial number."""
        raise NotImplementedError
```

---

## Build & Distribution

### Windows Executable
- Built with **PyInstaller** (single-file exe)
- Python bundled, no install required
- Target: Windows 10/11 x64
- ~30-50MB total
- Runs offline, no admin required

### Installer (Inno Setup)
- `radiocodes.iss` produces installer
- Installs to `C:\Program Files\RadioUnlock\`
- Start menu shortcut
- Uninstaller included
- Optional desktop shortcut

### Distribution
- GitHub Releases page
- Direct download of `RadioUnlock-Setup.exe`
- No account required to download

---

## Quality Bar

- [ ] Every supported brand has a **confirmed test vector** (known serial → known code)
- [ ] Invalid serial format shows clear error ("Serial should be 6 digits")
- [ ] All buttons work, no dead UI elements
- [ ] Code display shows correct number of digit boxes for the selected brand
- [ ] Copy button copies code to clipboard
- [ ] Help panel shows correct serial location for selected brand
- [ ] App starts in <3 seconds
- [ ] Runs fully offline
- [ ] Dark theme looks good, readable
- [ ] Installer works cleanly, uninstall removes everything
