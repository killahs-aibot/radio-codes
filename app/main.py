# -*- coding: utf-8 -*-
"""
RadioUnlock — Free Car Radio Code Calculator
Flet mobile/web app. Runs as Android APK, iOS app, or web browser.

Run locally:
  cd app
  flet run                          # desktop
  flet run --web                    # web browser

Build APK:
  flet build app/main.py --artifact apk
"""

import flet as ft
from flet import (
    Column, Container, ElevatedButton, Text,
    TextField, Row, View, Page, NavigationBar,
    NavigationDestination, Wrap, Icon, TextField
)
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from radiocodes.algorithms import (
    FordMAlgorithm, FordVAlgorithm, RenaultAlgorithm,
    VWRCDAlgorithm, VauxhallAlgorithm, FiatAlgorithm,
    NissanAlgorithm, HondaAlgorithm, KiaAlgorithm,
    PeugeotAlgorithm, AlfaAlgorithm, ChryslerAlgorithm
)
from radiocodes.lookup_engine import load_csv, get_stats
from radiocodes.serial_detector import detect_brand, get_format_hint

load_csv()
STATS = get_stats()
DB_TOTAL = STATS["total_pairs"]
DB_BRANDS = len(STATS["brands"])

# Colours
BG = "#0D1117"
SURFACE = "#161B22"
CARD_BG = "#1C2128"
ACCENT = "#238636"
ACCENT2 = "#1F6FEB"
TEXT = "#E6EDF3"
TEXT_MUTED = "#7D8590"
BORDER = "#30363D"
RED = "#F85149"
GREEN = "#3FB950"
ORANGE = "#D29922"

# Brand registry: (key, label, emoji, status, algo_class)
BRANDS = [
    ("ford_m", "Ford M-Series", "🚗", "✅", FordMAlgorithm),
    ("ford_v", "Ford V-Series", "🚗", "✅", FordVAlgorithm),
    ("renault", "Renault / Dacia", "🔧", "✅", RenaultAlgorithm),
    ("kia", "Kia", "🚙", "✅", KiaAlgorithm),
    ("vw", "VW / Audi / Seat", "🚘", "⚠️", VWRCDAlgorithm),
    ("opel", "Vauxhall / Opel", "🔧", "⚠️", VauxhallAlgorithm),
    ("fiat", "Fiat / Alfa Romeo", "🚗", "✅", FiatAlgorithm),
    ("peugeot", "Peugeot / Citroen", "🚗", "⚠️", PeugeotAlgorithm),
    ("nissan", "Nissan", "🚙", "⚠️", NissanAlgorithm),
    ("honda", "Honda / Acura", "🚗", "🏁", HondaAlgorithm),
    ("alfa", "Alfa Romeo", "🚗", "⚠️", AlfaAlgorithm),
    ("chrysler", "Chrysler / Jeep / Dodge", "🚙", "⚠️", ChryslerAlgorithm),
]

BRAND_HELP = {
    "ford_m": "Serial starts with M + 6 digits (e.g. M025345 → code 3306)",
    "ford_v": "Serial starts with V + 6 digits (e.g. V007337 → code 6500)",
    "renault": "Pre-code: 1 letter + 3 digits (e.g. D123 → 4216)",
    "kia": "Serial: letter A-H + 3 digits (e.g. H050 → 96160, B777 → 5808)",
    "vw": "Full 14-char serial (e.g. VWZ5Z7B5013069)",
    "opel": "Serial starts with GM (e.g. GM020328268659)",
    "fiat": "Last 4 digits of serial (e.g. VP1-1234 → enter 1234)",
    "peugeot": "Serial on label (e.g. 815BP730198502964)",
    "nissan": "12-char serial from radio screen",
    "honda": "🌐 OFFICIAL FREE: radio-navicode.honda.com\nEnter VIN + radio serial — free, official, always works!",
    "alfa": "Serial on radio label (often starts with BP or model number)",
    "chrysler": "4-6 character serial, often Uconnect navi serial",
}

ALGO_MAP = {key: algo_class() for key, _, _, _, algo_class in BRANDS}

STATUS_COLORS = {"✅": GREEN, "⚠️": ORANGE, "🏁": ACCENT2}


# ── App ──────────────────────────────────────────────────────────────────
def main(page: Page):
    page.title = "RadioUnlock"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    page.selected_brand = None

    # Refs
    serial_input = ft.Ref[TextField]()
    result_text = ft.Ref[Text]()
    status_text = ft.Ref[Text]()
    help_text = ft.Ref[Text]()
    detect_hint_text = ft.Ref[Text]()
    result_card = ft.Ref[Container]()

    # Brand button style refs (one per brand)
    brand_btn_refs = {key: ft.Ref[ElevatedButton]() for key, _, _, _, _ in BRANDS}

    def select_brand(key):
        page.selected_brand = key
        for k, ref in brand_btn_refs.items():
            btn = ref.current
            if btn:
                btn.style.bgcolor = ACCENT2 if k == key else SURFACE
                btn.style.color = TEXT if k != key else TEXT
                btn.update()
        help_text.current.value = BRAND_HELP.get(key, "")
        help_text.current.update()
        result_card.current.visible = False
        result_card.current.update()

    def make_brand_btn(key, label, emoji, status):
        color = STATUS_COLORS.get(status, TEXT_MUTED)
        ref = brand_btn_refs[key]

        def on_click(e):
            select_brand(key)

        btn = ElevatedButton(
            ref=ref,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=SURFACE,
                color=TEXT,
                padding=ft.padding.all(10),
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            content=Column([
                Text(emoji, size=18, text_align=ft.TextAlign.CENTER),
                Text(label, size=10, weight=ft.FontWeight.W_600,
                     text_align=ft.TextAlign.CENTER),
                Text(status, size=9, color=color),
            ], spacing=1, alignment=ft.MainAxisAlignment.CENTER),
        )
        return btn

    # Serial input
    def on_serial_change(e):
        serial = (e.control.value or "").strip()
        if len(serial) >= 3:
            detected, conf = detect_brand(serial)
            if detected and conf >= 0.6:
                hint = get_format_hint(serial)
                detect_hint_text.current.value = f"🔍 Detected: {detected} ({conf:.0%})"
                detect_hint_text.current.color = GREEN
            elif detected:
                hint = get_format_hint(serial)
                detect_hint_text.current.value = f"💡 {hint}"
                detect_hint_text.current.color = TEXT_MUTED
            else:
                detect_hint_text.current.value = f"💡 {get_format_hint(serial)}"
                detect_hint_text.current.color = TEXT_MUTED
        else:
            detect_hint_text.current.value = ""
        detect_hint_text.current.update()

    serial_field = TextField(
        ref=serial_input,
        label="Radio Serial Number",
        hint_text="Enter serial number...",
        bgcolor=SURFACE,
        border_color=BORDER,
        focused_border_color=ACCENT2,
        label_style=ft.TextStyle(color=TEXT_MUTED),
        text_style=ft.TextStyle(color=TEXT, size=18),
        on_change=on_serial_change,
        on_submit=lambda e: calculate(),
    )

    # Result display
    result_container = Container(
        ref=result_card,
        content=Column([
            Text("——", ref=result_text, size=56, weight=ft.FontWeight.W_900,
                 font_family="monospace", color=TEXT, text_align=ft.TextAlign.CENTER),
            Text("Enter serial and tap Calculate", ref=status_text,
                 size=12, color=TEXT_MUTED, text_align=ft.TextAlign.CENTER),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
        padding=ft.padding.symmetric(vertical=28, horizontal=20),
        border_radius=16,
        bgcolor=CARD_BG,
        border=ft.border.all(1, BORDER),
        visible=False,
    )

    def calculate():
        key = page.selected_brand
        serial = (serial_input.current.value or "").strip()

        if not key:
            page.show_snack_bar(ft.SnackBar(content=Text("⚠️ Tap a brand first"), bgcolor=ORANGE))
            return
        if not serial:
            page.show_snack_bar(ft.SnackBar(content=Text("⚠️ Enter the serial number"), bgcolor=ORANGE))
            return

        algo = ALGO_MAP.get(key)
        if not algo:
            return

        is_valid, err = algo.validate_serial(serial)
        if not is_valid:
            result_card.current.visible = True
            result_text.current.value = "???"
            result_text.current.color = RED
            status_text.current.value = f"Invalid: {err}"
            status_text.current.color = RED
            result_card.current.update()
            return

        try:
            code = algo.calculate(serial)
            result_card.current.visible = True
            result_text.current.value = code
            result_text.current.color = GREEN
            status_text.current.value = f"✅ Code found!"
            status_text.current.color = GREEN
            result_card.current.update()
        except ValueError as err:
            result_card.current.visible = True
            result_text.current.value = "NOT FOUND"
            result_text.current.color = TEXT_MUTED
            status_text.current.value = str(err)[:120]
            status_text.current.color = TEXT_MUTED
            result_card.current.update()

    def copy_code(e):
        code = result_text.current.value if result_text.current else ""
        if code and code not in ("——", "???", "NOT FOUND"):
            page.set_clipboard(code)
            page.show_snack_bar(ft.SnackBar(
                content=Text(f"📋 {code} copied!"),
                bgcolor=GREEN,
            ))

    # Navigation — 3 tabs
    nav = NavigationBar(
        destinations=[
            NavigationDestination(icon=ft.Icons.CALCULATE, label="Calculator"),
            NavigationDestination(icon=ft.Icons.MEMORY, label="EEPROM"),
            NavigationDestination(icon=ft.Icons.INFO_OUTLINE, label="About"),
        ],
        bgcolor=SURFACE,
        indicator_color=ACCENT2,
        on_change=lambda e: (
            page.go("/eeprom") if e.data == "1" else page.go("/") if e.data == "0" else page.go("/about")
        ),
    )
    page.navigation_bar = nav

    # Brand buttons grid (3 per row on desktop, 2 on mobile)
    brand_button_widgets = [
        make_brand_btn(key, label, emoji, status)
        for key, label, emoji, status, _ in BRANDS
    ]

    # Wrap brand buttons in rows of 3
    brand_rows = []
    for i in range(0, len(brand_button_widgets), 3):
        chunk = brand_button_widgets[i:i+3]
        # Fill remaining slots with invisible containers
        while len(chunk) < 3:
            chunk.append(Container(width=100))
        brand_rows.append(
            Row(chunk, alignment=ft.MainAxisAlignment.CENTER, spacing=6)
        )

    # ── Home view ──────────────────────────────────────────────────────
    home_view = View(
        "/",
        scroll=ft.ScrollMode.AUTO,
        [
            Container(
                padding=16,
                bgcolor=BG,
                content=Column([
                    # Header
                    Row([
                        Text("📻 RadioUnlock", size=22, weight=ft.FontWeight.W_800, color=TEXT),
                        Icon(ft.Icons.RADIO, color=ACCENT2, size=22),
                        Container(expand=True),
                        Text(f"🔍 {DB_TOTAL} codes", size=12,
                             color=GREEN, weight=ft.FontWeight.W_600),
                    ]),
                    Text("Free car radio codes · Works offline · No ads",
                         size=11, color=TEXT_MUTED),
                    Container(height=14),

                    # Step 1: Brand
                    Text("1️⃣ SELECT BRAND", size=11, weight=ft.FontWeight.W_700,
                         color=TEXT_MUTED),
                    Container(height=6),
                    # Brand grid
                    *brand_rows,
                    Container(height=14),

                    # Step 2: Serial
                    Text("2️⃣ ENTER SERIAL", size=11, weight=ft.FontWeight.W_700,
                         color=TEXT_MUTED),
                    Container(height=6),
                    serial_field,
                    Container(height=4),
                    Text("", ref=detect_hint_text, size=10, color=TEXT_MUTED),
                    Container(height=10),

                    ElevatedButton(
                        text="🔓 CALCULATE CODE",
                        on_click=lambda e: calculate(),
                        style=ft.ButtonStyle(
                            bgcolor=ACCENT, color=ft.WHITE, padding=16,
                            shape=ft.RoundedRectangleBorder(radius=12),
                        ),
                        width=float("inf"),
                    ),
                    Container(height=14),

                    # Result
                    result_container,

                    # Copy button
                    Row(
                        [ElevatedButton(
                            text="📋 Copy Code",
                            on_click=copy_code,
                            style=ft.ButtonStyle(
                                bgcolor=CARD_BG, color=TEXT, padding=10,
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        )],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),

                    # Help text
                    Container(height=6),
                    Text("", ref=help_text, size=11,
                         color=TEXT_MUTED, italic=True),
                ], spacing=0),
            ),
        ],
    )

    # ── About view ─────────────────────────────────────────────────────
    about_view = View(
        "/about",
        scroll=ft.ScrollMode.AUTO,
        [
            Container(
                padding=16,
                bgcolor=BG,
                content=Column([
                    Row([
                        Text("📻 RadioUnlock", size=24, weight=ft.FontWeight.W_700, color=TEXT),
                    ]),
                    Text("Free car radio codes · No ads · No paywalls · No internet needed",
                         size=12, color=TEXT_MUTED),
                    Container(height=16),

                    # Stats
                    Container(
                        padding=20,
                        border_radius=16,
                        bgcolor=ACCENT,
                        content=Row([
                            Column([
                                Text(f"{DB_TOTAL}", size=42, weight=ft.FontWeight.W_700, color=ft.WHITE),
                                Text("free codes", size=13, color=ft.WHITE),
                            ]),
                            Container(width=32),
                            Column([
                                Text(f"{DB_BRANDS}", size=42, weight=ft.FontWeight.W_700, color=ft.WHITE),
                                Text("car brands", size=13, color=ft.WHITE),
                            ]),
                        ], spacing=16),
                    ),
                    Container(height=16),

                    # ✅ Algorithms
                    Container(
                        padding=14,
                        border_radius=12,
                        bgcolor=CARD_BG,
                        border=ft.border.all(1, BORDER),
                        content=Column([
                            Text("✅ INSTANT — works offline",
                                 size=13, weight=ft.FontWeight.W_600, color=GREEN),
                            Container(height=6),
                            Text("Ford M-Series  ·  Ford V-Series  ·  Renault  ·  Kia",
                                 size=12, color=TEXT, font_family="monospace"),
                            Text("Fiat / Alfa Romeo VP1/VP2",
                                 size=12, color=TEXT, font_family="monospace"),
                            Container(height=4),
                            Text("Enter serial → get code instantly → no internet needed",
                                 size=11, color=TEXT_MUTED, italic=True),
                        ], spacing=4),
                    ),
                    Container(height=10),

                    # ⚠️ Lookup
                    Container(
                        padding=14,
                        border_radius=12,
                        bgcolor=CARD_BG,
                        border=ft.border.all(1, BORDER),
                        content=Column([
                            Text("⚠️ DATABASE LOOKUP — enter exact serial",
                                 size=13, weight=ft.FontWeight.W_600, color=ORANGE),
                            Container(height=6),
                            Text("VW / Audi / Seat / Skoda",
                                 size=12, color=TEXT, font_family="monospace"),
                            Text("Vauxhall / Opel  ·  Peugeot / Citroen",
                                 size=12, color=TEXT, font_family="monospace"),
                            Text("Nissan  ·  Alfa Romeo  ·  Chrysler / Jeep",
                                 size=12, color=TEXT, font_family="monospace"),
                            Container(height=4),
                            Text("Your serial must match our database exactly",
                                 size=11, color=TEXT_MUTED, italic=True),
                        ], spacing=4),
                    ),
                    Container(height=10),

                    # 🏁 Free portals
                    Container(
                        padding=14,
                        border_radius=12,
                        bgcolor=CARD_BG,
                        border=ft.border.all(1, BORDER),
                        content=Column([
                            Text("🏁 FREE OFFICIAL PORTALS — use these first!",
                                 size=13, weight=ft.FontWeight.W_600, color=ACCENT2),
                            Container(height=6),
                            Text("Honda: radio-navicode.honda.com",
                                 size=12, color=ACCENT2, font_family="monospace"),
                            Text("Acura: radio-navicode.acura.com",
                                 size=12, color=ACCENT2, font_family="monospace"),
                            Text("Nissan USA: radio-navicode.nissan.com",
                                 size=12, color=ACCENT2, font_family="monospace"),
                            Container(height=4),
                            Text("Enter VIN + radio serial — free, official, always works",
                                 size=11, color=TEXT_MUTED, italic=True),
                        ], spacing=4),
                    ),
                    Container(height=16),

                    # Legend
                    Container(
                        padding=12,
                        border_radius=10,
                        bgcolor=SURFACE,
                        content=Row(wrap=True, controls=[
                            Text("Legend: ", size=11, color=TEXT_MUTED, weight=ft.FontWeight.W_600),
                            Text("✅ ", size=11, color=GREEN),
                            Text("algorithm  ", size=11, color=TEXT),
                            Text("⚠️ ", size=11, color=ORANGE),
                            Text("lookup  ", size=11, color=TEXT),
                            Text("🏁 ", size=11, color=ACCENT2),
                            Text("official portal", size=11, color=TEXT),
                        ]),
                    ),
                    Container(height=16),

                    # How to find serial
                    Container(
                        padding=14,
                        border_radius=12,
                        bgcolor=CARD_BG,
                        border=ft.border.all(1, BORDER),
                        content=Column([
                            Text("📋 How to find your serial number:",
                                 size=13, weight=ft.FontWeight.W_600, color=TEXT),
                            Container(height=8),
                            Text("1️⃣ Power on radio — display shows 'CODE' or 'LOCKED'",
                                 size=12, color=TEXT),
                            Text("2️⃣ Press and hold 'AS' or 'SYNC' button for 2+ seconds",
                                 size=12, color=TEXT),
                            Text("3️⃣ Serial appears on screen or on the radio label",
                                 size=12, color=TEXT),
                            Text("4️⃣ On some radios, serial is on a sticker on the chassis",
                                 size=12, color=TEXT),
                            Text("5️⃣ For Peugeot/Citroen: remove radio, serial on label",
                                 size=12, color=TEXT),
                        ], spacing=5),
                    ),
                    Container(height=12),

                    Text("Built by Killah · Open source · No tracking · No ads",
                         size=11, color=TEXT_MUTED, text_align=ft.TextAlign.CENTER),
                ], spacing=0),
            ),
        ],
    )

    # ── EEPROM view ───────────────────────────────────────────────────
    eeprom_result_text = ft.Ref[ft.Text]()
    eeprom_status_text = ft.Ref[ft.Text]()
    eeprom_result_card = ft.Ref[ft.Container]()
    eeprom_model_dropdown = ft.Ref[ft.Dropdown]()

    def on_eeprom_analyze(e):
        # File picker would go here — for web, we use a text area for hex paste
        eeprom_status_text.current.value = "Paste a hex dump or load a .bin file to analyze."
        eeprom_status_text.current.color = TEXT_MUTED
        eeprom_result_card.current.visible = False
        eeprom_result_card.current.update()
        eeprom_status_text.current.update()

    eeprom_view = ft.View(
        "/eeprom",
        scroll=ft.ScrollMode.AUTO,
        [
            ft.Container(
                padding=16,
                bgcolor=BG,
                content=ft.Column([
                    ft.Row([
                        ft.Text("💾", size=26),
                        ft.Text("EEPROM Dump Analyzer", size=24, weight=ft.FontWeight.W_700, color=TEXT),
                    ], spacing=8),
                    ft.Text("Extract codes from radio EEPROM dumps — works for ALL brands",
                            size=12, color=TEXT_MUTED),
                    ft.Container(height=14),

                    # How it works
                    ft.Container(
                        padding=14,
                        border_radius=12,
                        bgcolor=CARD_BG,
                        border=ft.border.all(1, BORDER),
                        content=ft.Column([
                            ft.Text("📋 How to get your EEPROM dump:",
                                    size=14, weight=ft.FontWeight.W_600, color=TEXT),
                            ft.Container(height=8),
                            ft.Text("1️⃣  Remove radio from dashboard", size=13, color=TEXT),
                            ft.Text("2️⃣  Locate the 8-pin SOIC chip (marked 24C01–24C64)", size=13, color=TEXT),
                            ft.Text("3️⃣  Solder to CH341A USB programmer (~£5 on eBay)", size=13, color=TEXT),
                            ft.Text("4️⃣  Read with flashrom or CH341A software → save .bin", size=13, color=TEXT),
                            ft.Text("5️⃣  Load the .bin file here → get your code", size=13, color=TEXT),
                        ], spacing=6),
                    ),
                    ft.Container(height=12),

                    # Supported chips
                    ft.Container(
                        padding=14,
                        border_radius=12,
                        bgcolor=CARD_BG,
                        border=ft.border.all(1, BORDER),
                        content=ft.Column([
                            ft.Text("📡 Supported EEPROM chips:",
                                    size=14, weight=ft.FontWeight.W_600, color=TEXT),
                            ft.Container(height=8),
                            ft.Text("24C01  ·  24C02  ·  24C04  ·  24C08  ·  24C16  ·  24C64",
                                    size=13, color=ACCENT2, font_family="monospace"),
                            ft.Container(height=8),
                            ft.Text("Supported radios:", size=12, color=TEXT_MUTED),
                            ft.Text("Blaupunkt CAR2003/2004/300/CD300",
                                    size=12, color=TEXT_MUTED),
                            ft.Text("Ford 6000CD · M-Series · TravelPilot",
                                    size=12, color=TEXT_MUTED),
                            ft.Text("Opel/Vauxhall CDC/CDX/Navi",
                                    size=12, color=TEXT_MUTED),
                            ft.Text("Renault · VW RCD 300/310/510 · Nissan Connect",
                                    size=12, color=TEXT_MUTED),
                            ft.Text("Honda/Acura · Fiat Uconnect · Bosch Touch & Connect",
                                    size=12, color=TEXT_MUTED),
                        ], spacing=4),
                    ),
                    ft.Container(height=12),

                    # Radio model selector
                    ft.Text("Radio Model / Chip:", size=13, weight=ft.FontWeight.W_600, color=TEXT),
                    ft.Container(height=6),
                    ft.Dropdown(
                        ref=eeprom_model_dropdown,
                        options=[
                            ft.DropdownOption("FULL SCAN"),
                            ft.DropdownOption("FULL SCAN 5-digit"),
                            ft.DropdownOption("Blaupunkt CAR2003"),
                            ft.DropdownOption("Blaupunkt CAR2004"),
                            ft.DropdownOption("Blaupunkt CAR300"),
                            ft.DropdownOption("Blaupunkt CD300"),
                            ft.DropdownOption("Opel / Vauxhall CDX"),
                            ft.DropdownOption("Opel / Vauxhall CDC"),
                            ft.DropdownOption("Opel / Vauxhall Navi"),
                            ft.DropdownOption("Ford 6000CD"),
                            ft.DropdownOption("Ford M-Series"),
                            ft.DropdownOption("Renault / Dacia"),
                            ft.DropdownOption("VW RCD 300"),
                            ft.DropdownOption("VW RCD 310"),
                            ft.DropdownOption("VW RCD 510"),
                            ft.DropdownOption("Audi Chorus / Concert / Symphony"),
                            ft.DropdownOption("Fiat Uconnect"),
                            ft.DropdownOption("Alfa Romeo Connect"),
                            ft.DropdownOption("Nissan Connect"),
                            ft.DropdownOption("Nissan Patrol / Qashqai"),
                            ft.DropdownOption("Honda / Acura"),
                            ft.DropdownOption("Bosch Touch & Connect"),
                            ft.DropdownOption("Siemens VDO CR500"),
                        ],
                        value="FULL SCAN",
                        bgcolor=SURFACE,
                        border_color=BORDER,
                        focused_border_color=ACCENT2,
                        label_style=ft.TextStyle(color=TEXT_MUTED),
                    ),
                    ft.Container(height=12),

                    # File load info
                    ft.Container(
                        padding=14,
                        border_radius=12,
                        bgcolor=CARD_BG,
                        border=ft.border.all(1, BORDER),
                        content=ft.Column([
                            ft.Text("💾 Load your EEPROM dump:",
                                    size=14, weight=ft.FontWeight.W_600, color=TEXT),
                            ft.Container(height=8),
                            ft.Text("Desktop app required to load .bin files directly.",
                                    size=12, color=TEXT_MUTED),
                            ft.Text("CH341A programmer + flashrom = free EEPROM reader.",
                                    size=12, color=TEXT_MUTED),
                            ft.Container(height=6),
                            ft.Text("Web version: paste hex bytes below (e.g. 01 02 03 04...)",
                                    size=11, color=TEXT_MUTED),
                        ], spacing=4),
                    ),
                    ft.Container(height=12),

                    # Result display
                    ft.Container(
                        ref=eeprom_result_card,
                        visible=False,
                        padding=16,
                        border_radius=12,
                        bgcolor=CARD_BG,
                        border=ft.border.all(1, BORDER),
                        content=ft.Column([
                            ft.Text("💾 Results:", size=14, weight=ft.FontWeight.W_600, color=TEXT),
                            ft.Container(height=8),
                            ft.Text("", ref=eeprom_result_text, size=14,
                                    color=GREEN, font_family="monospace"),
                            ft.Container(height=4),
                            ft.Text("", ref=eeprom_status_text, size=12, color=TEXT_MUTED),
                        ], spacing=4),
                    ),

                    ft.Container(height=16),

                    # Recommended programmer
                    ft.Container(
                        padding=14,
                        border_radius=12,
                        bgcolor=ACCENT,
                        content=ft.Column([
                            ft.Text("🔧 Recommended programmer:",
                                    size=14, weight=ft.FontWeight.W_600, color=ft.WHITE),
                            ft.Container(height=6),
                            ft.Text("CH341A USB programmer — ~£5 on eBay / Amazon",
                                    size=12, color=ft.WHITE),
                            ft.Text("Works on Windows, macOS, and Linux",
                                    size=12, color=ft.WHITE),
                            ft.Text("Software: flashrom (free) · ch341a programmer tool",
                                    size=12, color=ft.WHITE),
                        ], spacing=4),
                    ),
                ], spacing=0),
            ),
        ],
    )

    page.add(home_view)
    page.add(eeprom_view)
    page.add(about_view)

    def on_route(e):
        home_view.visible = page.route == "/"
        eeprom_view.visible = page.route == "/eeprom"
        about_view.visible = page.route == "/about"
        page.update()

    page.on_route_change = on_route
    page.go("/")
