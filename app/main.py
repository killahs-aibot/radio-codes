# -*- coding: utf-8 -*-
"""
RadioUnlock — Free Car Radio Code Calculator
Flet mobile/web app. Runs as Android APK, iOS app, or web browser.

Run locally:
  cd app
  flet run                          # desktop
  flet run --web                    # web browser
  flet run --android --debug        # android (requires Android SDK)

Build APK:
  flet pack --android app/main.py
"""

import flet as ft
from flet import (
    AppView, Column, Container, ElevatedButton, Text,
    TextField, Row, Icon, Dropdown, DropdownOption,
    NavigationBar, NavigationDestination, View, Page
)
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from radiocodes.algorithms import (
    FordMAlgorithm, FordVAlgorithm, RenaultAlgorithm,
    VWRCDAlgorithm, VauxhallAlgorithm, FiatAlgorithm,
    NissanAlgorithm, HondaAlgorithm
)
from radiocodes.lookup_engine import load_csv, get_stats

# Load database
load_csv()
STATS = get_stats()
DB_TOTAL = STATS["total_pairs"]
DB_BRANDS = len(STATS["brands"])

# Algorithm registry
ALGORITHMS = {
    "Ford M-Series ✅": FordMAlgorithm(),
    "Ford V-Series ✅": FordVAlgorithm(),
    "Renault / Dacia ✅": RenaultAlgorithm(),
    "VW / Audi / Seat / Skoda ⚠️": VWRCDAlgorithm(),
    "Vauxhall / Opel ⚠️": VauxhallAlgorithm(),
    "Fiat / Alfa Romeo ✅": FiatAlgorithm(),
    "Nissan ⚠️ UNVERIFIED": NissanAlgorithm(),
    "Honda 🏁 FREE PORTAL": HondaAlgorithm(),
    "Acura 🏁 FREE PORTAL": HondaAlgorithm(),  # Same portal as Honda
}

BRAND_HELP = {
    "Ford M-Series ✅": "Enter serial starting with M (e.g. M025345)",
    "Ford V-Series ✅": "Enter serial starting with V (e.g. V528803)",
    "Renault / Dacia ✅": "Enter pre-code: 1 letter + 3 digits (e.g. D123)",
    "VW / Audi / Seat / Skoda ⚠️": "Enter full 14-char serial (e.g. VWZ5Z7B5013069)",
    "Vauxhall / Opel ⚠️": "Enter serial starting with GM (e.g. GM020328268659)",
    "Fiat / Alfa Romeo ✅": "Enter last 4 digits of serial (e.g. VP1-1234 → enter 1234)",
    "Nissan ⚠️ UNVERIFIED": "⚠️ Formula unverified. Try serial or use FREE portal: radio-navicode.nissan.com",
    "Honda 🏁 FREE PORTAL": "🌐 OFFICIAL FREE: radio-navicode.honda.com\nEnter VIN + radio serial, get code instantly — free!",
    "Acura 🏁 FREE PORTAL": "🌐 OFFICIAL FREE: radio-navicode.acura.com\nSame as Honda — Enter VIN + radio serial, get code instantly",
}

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


# ── App ──────────────────────────────────────────────────────────────────
def main(page: Page):
    page.title = "RadioUnlock"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    page.navigation_bar = None  # Set after first view

    # State refs
    selected_brand = ft.Ref[Dropdown]()
    serial_input = ft.Ref[TextField]()
    result_text = ft.Ref[Text]()
    status_text = ft.Ref[Text]()
    help_text = ft.Ref[Text]()
    result_card = ft.Ref[Container]()

    # ── Home view ──────────────────────────────────────────────────────
    brand_dropdown = Dropdown(
        ref=selected_brand,
        label="Select Car Brand",
        hint_text="Choose your radio brand...",
        options=[DropdownOption(k) for k in ALGORITHMS.keys()],
        bgcolor=SURFACE,
        border_color=BORDER,
        focused_border_color=ACCENT2,
        label_style=ft.TextStyle(color=TEXT_MUTED),
    )

    serial_field = TextField(
        ref=serial_input,
        label="Radio Serial Number",
        hint_text="Enter serial number...",
        bgcolor=SURFACE,
        border_color=BORDER,
        focused_border_color=ACCENT2,
        label_style=ft.TextStyle(color=TEXT_MUTED),
        text_style=ft.TextStyle(color=TEXT, size=18),
    )

    result_container = Container(
        ref=result_card,
        content=Column([
            Text("——", ref=result_text, size=48, weight=ft.FontWeight.W_700,
                 font_family="monospace", color=TEXT, text_align=ft.TextAlign.CENTER),
            Text("Enter serial and tap Calculate", ref=status_text,
                 size=12, color=TEXT_MUTED, text_align=ft.TextAlign.CENTER),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
        padding=30,
        border_radius=16,
        bgcolor=CARD_BG,
        border=ft.border.all(1, BORDER),
        visible=False,
    )

    def on_brand_change(e):
        brand = selected_brand.current.value if selected_brand.current else None
        if brand and brand in BRAND_HELP:
            help_text.current.value = BRAND_HELP[brand]
            help_text.current.update()

    brand_dropdown.on_change = on_brand_change

    def calculate(e):
        brand_key = selected_brand.current.value if selected_brand.current else None
        serial = serial_input.current.value or "" if serial_input.current else ""

        if not brand_key:
            page.show_snack_bar(ft.SnackBar(content=Text("⚠️ Select a brand first")))
            return
        if not serial.strip():
            page.show_snack_bar(ft.SnackBar(content=Text("⚠️ Enter a serial number")))
            return

        algo = ALGORITHMS.get(brand_key)
        if not algo:
            return

        # Validate
        is_valid, err = algo.validate_serial(serial.strip())
        if not is_valid:
            result_card.current.visible = True
            result_text.current.value = "???"
            result_text.current.color = RED
            status_text.current.value = f"Invalid serial: {err}"
            status_text.current.color = RED
            result_card.current.update()
            return

        # Calculate
        try:
            code = algo.calculate(serial.strip())
            result_card.current.visible = True
            result_text.current.value = code
            result_text.current.color = GREEN
            status_text.current.value = f"✅ {brand_key} — Code found!"
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
            page.show_snack_bar(ft.SnackBar(content=Text(f"📋 {code} copied!")))

    home_view = View(
        "/",
        [
            Container(
                padding=16,
                bgcolor=BG,
                content=Column(
                    [
                        # Header
                        Row([
                            Text("📻 RadioUnlock", size=24, weight=ft.FontWeight.W_700, color=TEXT),
                            Icon(ft.Icons.RADIO, color=ACCENT2),
                        ], spacing=8),
                        Text("Free car radio codes · No ads · No paywalls",
                             size=12, color=TEXT_MUTED),
                        Container(height=20),

                        # Dropdown + input stacked
                        brand_dropdown,
                        Container(height=12),
                        serial_field,
                        Container(height=16),

                        # Calculate
                        ElevatedButton(
                            text="🔓 CALCULATE CODE",
                            on_click=calculate,
                            style=ft.ButtonStyle(
                                bgcolor=ACCENT, color=ft.WHITE, padding=14,
                                shape=ft.RoundedRectangleBorder(radius=12),
                            ),
                            width=700,
                        ),
                        Container(height=16),

                        # Result
                        result_container,

                        # Copy button (shown when result visible)
                        Row([
                            ElevatedButton(
                                text="📋 Copy Code",
                                on_click=copy_code,
                                style=ft.ButtonStyle(
                                    bgcolor=CARD_BG, color=TEXT, padding=10,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER),

                        # Help
                        Text("", ref=help_text, size=12,
                             color=TEXT_MUTED, italic=True),

                        Container(height=16),

                        # DB badge
                        Row([
                            Text("🔍", size=14),
                            Text(f"{DB_TOTAL}", size=16, weight=ft.FontWeight.W_700, color=GREEN),
                            Text(f"free codes across {DB_BRANDS} brands",
                                 size=13, color=TEXT_MUTED),
                        ], alignment=ft.MainAxisAlignment.CENTER),

                        Container(height=8),
                        Text("💾 EEPROM Reader in About tab →",
                             size=11, color=TEXT_MUTED),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    spacing=0,
                ),
            ),
        ],
    )

    # ── EEPROM view ────────────────────────────────────────────────────
    eeprom_view = View(
        "/eeprom",
        [
            Container(
                padding=16,
                bgcolor=BG,
                content=Column(
                    [
                        Row([
                            Text("💾 EEPROM Reader", size=24, weight=ft.FontWeight.W_700, color=TEXT),
                        ]),
                        Text("Extract code directly from radio's memory chip",
                             size=12, color=TEXT_MUTED),
                        Container(height=16),

                        # How to
                        Container(
                            padding=14,
                            border_radius=12,
                            bgcolor=CARD_BG,
                            border=ft.border.all(1, BORDER),
                            content=Column([
                                Text("📋 How to get your EEPROM dump:",
                                     size=14, weight=ft.FontWeight.W_600, color=TEXT),
                                Container(height=8),
                                Text("1️⃣ Remove radio from dashboard", size=13, color=TEXT),
                                Text("2️⃣ Find the 8-pin SOIC chip (marked 24Cxx)", size=13, color=TEXT),
                                Text("3️⃣ Solder to CH341A programmer (~£5)", size=13, color=TEXT),
                                Text("4️⃣ Read with flashrom or CH341A software", size=13, color=TEXT),
                                Text("5️⃣ Save as .bin — load in desktop app", size=13, color=TEXT),
                            ], spacing=6),
                        ),
                        Container(height=12),

                        # Chips
                        Container(
                            padding=14,
                            border_radius=12,
                            bgcolor=CARD_BG,
                            border=ft.border.all(1, BORDER),
                            content=Column([
                                Text("📡 Supported EEPROM chips:",
                                     size=14, weight=ft.FontWeight.W_600, color=TEXT),
                                Container(height=8),
                                Text("24C01 · 24C02 · 24C04 · 24C08 · 24C16 · 24C64",
                                     size=13, color=ACCENT2, font_family="monospace"),
                                Container(height=8),
                                Text("Supported radios:", size=12, color=TEXT_MUTED),
                                Text("Blaupunkt CAR2003/2004/300/CD300", size=12, color=TEXT_MUTED),
                                Text("Siemens VDO CR500", size=12, color=TEXT_MUTED),
                                Text("Ford 6000CD · M-Series", size=12, color=TEXT_MUTED),
                                Text("Bosch Touch & Connect", size=12, color=TEXT_MUTED),
                                Text("Renault · VW RCD · Nissan Connect", size=12, color=TEXT_MUTED),
                            ], spacing=4),
                        ),
                        Container(height=12),

                        # Programmer
                        Container(
                            padding=14,
                            border_radius=12,
                            bgcolor=CARD_BG,
                            border=ft.border.all(1, BORDER),
                            content=Column([
                                Text("🔧 Recommended programmer:",
                                     size=14, weight=ft.FontWeight.W_600, color=TEXT),
                                Container(height=8),
                                Text("CH341A USB programmer — ~£5 on eBay/Amazon", size=12, color=TEXT),
                                Text("Works on Windows, macOS, Linux", size=12, color=TEXT),
                                Text("Software: flashrom (free) or CH341A tool", size=12, color=TEXT),
                                Container(height=8),
                                Text("💡 The desktop app does full-chip BCD scan — finds codes "
                                     "even for unknown radio models",
                                     size=11, color=TEXT_MUTED, italic=True),
                            ], spacing=4),
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
        ],
    )

    # ── About view ─────────────────────────────────────────────────────
    about_view = View(
        "/about",
        [
            Container(
                padding=16,
                bgcolor=BG,
                content=Column(
                    [
                        Row([
                            Text("📻 RadioUnlock", size=24, weight=ft.FontWeight.W_700, color=TEXT),
                        ]),
                        Text("Free car radio codes · No ads · No paywalls",
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

                        # Algos — verified
                        Container(
                            padding=14,
                            border_radius=12,
                            bgcolor=CARD_BG,
                            border=ft.border.all(1, BORDER),
                            content=Column([
                                Text("✅ Working algorithms (instant, no internet):",
                                     size=13, weight=ft.FontWeight.W_600, color=GREEN),
                                Container(height=6),
                                Text("Ford M-Series · Ford V-Series · Renault / Dacia",
                                     size=12, color=TEXT, font_family="monospace"),
                                Text("Fiat / Alfa Romeo VP1/VP2",
                                     size=12, color=TEXT, font_family="monospace"),
                                Container(height=4),
                                Text("⚠️ Database lookup (may not find your serial):",
                                     size=11, weight=ft.FontWeight.W_600, color="FFA500"),
                                Text("VW/Audi/Seat/Skoda · Vauxhall/Opel",
                                     size=11, color=TEXT_MUTED, font_family="monospace"),
                                Text("⚠️ Unverified formula (try official portal first):",
                                     size=11, weight=ft.FontWeight.W_600, color="FFA500"),
                                Text("Nissan",
                                     size=11, color=TEXT_MUTED, font_family="monospace"),
                                Container(height=4),
                                Text("🌐 Free official portals (fast & guaranteed):",
                                     size=11, weight=ft.FontWeight.W_600, color=ACCENT2),
                                Text("Honda → radio-navicode.honda.com",
                                     size=11, color=TEXT_MUTED),
                                Text("Acura → radio-navicode.acura.com",
                                     size=11, color=TEXT_MUTED),
                                Text("Nissan → radio-navicode.nissan.com",
                                     size=11, color=TEXT_MUTED),
                           ], spacing=4),
                        ),
                        Container(height=8),

                        # DB brands
                        Container(
                            padding=14,
                            border_radius=12,
                            bgcolor=CARD_BG,
                            border=ft.border.all(1, BORDER),
                            content=Column([
                                Text("🔍 Free lookup database:",
                                     size=13, weight=ft.FontWeight.W_600, color=ACCENT2),
                                Container(height=6),
                                Text(
                                    "Renault · Kia · Ford · Opel · Hyundai · Blaupunkt · "
                                    "Fiat · Land Rover · Rover · Nissan · Mini · Audi · "
                                    "VW · Mercedes · Peugeot · and 27 more...",
                                    size=12, color=TEXT_MUTED,
                                ),
                            ], spacing=4),
                        ),
                        Container(height=16),

                        Text(
                            "Radio codes have been paywalled for 30 years.\n"
                            "This app is free forever. Share it.",
                            size=13, color=TEXT_MUTED, italic=True,
                        ),
                        Container(height=8),
                        Text(
                            "If it helped you — buy someone a coffee ☕",
                            size=12, color=TEXT_MUTED,
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
        ],
    )

    # ── Navigation ─────────────────────────────────────────────────────
    views = {"/": home_view, "/eeprom": eeprom_view, "/about": about_view}

    def on_nav(e: ft.NavigationEvent):
        idx = int(e.data.get("index", 0))
        routes = ["/", "/eeprom", "/about"]
        page.views.clear()
        page.views.append(views[routes[idx]]())
        page.navigation_bar.current_index = idx
        page.update()

    page.navigation_bar = NavigationBar(
        destinations=[
            NavigationDestination(icon=ft.Icons.CALCULATE, label="Calculator"),
            NavigationDestination(icon=ft.Icons.MEMORY, label="EEPROM"),
            NavigationDestination(icon=ft.Icons.INFO_OUTLINE, label="About"),
        ],
        on_change=on_nav,
        bgcolor=SURFACE,
        indicator_color=ACCENT2,
        selected_index=0,
    )

    page.views.append(home_view)
    page.update()


# ── Run ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ft.app(target=main, app_title="RadioUnlock", view=AppView.WEB_BROWSER)
