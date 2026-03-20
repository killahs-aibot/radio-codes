# -*- coding: utf-8 -*-
"""
RadioUnlock — Free Car Radio Code Calculator
A Flet mobile/web app. Works on Android, iOS, and browser.
"""

import flet as ft
from flet import (
    AppView, Column, Container, ElevatedButton, Text,
    TextField, Row, IconButton, Icon, Dropdown,
    Option, Switch, Card, ProgressBar, AdaptiveScaffold,
    NavigationBar, NavigationDestination, Page, View
)
import sys
import os

# Import our radio code engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from radiocodes.algorithms import (
    FordMAlgorithm, FordVAlgorithm, RenaultAlgorithm,
    VWRCDAlgorithm, VauxhallAlgorithm, PeugeotAlgorithm,
    FiatAlgorithm, NissanAlgorithm
)
from radiocodes.lookup_engine import load_csv, get_stats, lookup

# ── Load the lookup database ────────────────────────────────────────────
load_csv()
STATS = get_stats()
DB_TOTAL = STATS["total_pairs"]
DB_BRANDS = len(STATS["brands"])

# ── Algorithm registry ──────────────────────────────────────────────────
ALGORITHMS = {
    "Ford M-Series": FordMAlgorithm(),
    "Ford V-Series": FordVAlgorithm(),
    "Renault / Dacia": RenaultAlgorithm(),
    "VW / Audi / Seat / Skoda": VWRCDAlgorithm(),
    "Vauxhall / Opel": VauxhallAlgorithm(),
    "Peugeot / Citroën": PeugeotAlgorithm(),
    "Fiat / Alfa Romeo": FiatAlgorithm(),
    "Nissan": NissanAlgorithm(),
}

BRAND_HELP = {
    "Ford M-Series": "Serial: M123456\n(hold buttons 1+6 while turning on)",
    "Ford V-Series": "Serial: V123456\n(hold buttons 1+6 while turning on)",
    "Renault / Dacia": "Serial: D123\n(hold buttons 1+6 + POWER)",
    "VW RCD": "Serial: VWZ5Z7B5013069\n(hold FM2 + SCAN together)",
    "Vauxhall / Opel": "Serial: GM020328268659\n(enter wrong code 3x to see serial)",
    "Fiat / Alfa Romeo": "Last 4 digits of serial\n(e.g. VP1-1234 → enter 1234)",
    "Nissan": "Serial: CY16C-1234567\n(hold buttons 1+3 for 5 seconds)",
}


# ── Custom colors ───────────────────────────────────────────────────────
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


def main(page: Page):
    page.title = "RadioUnlock"
    page.theme_mode = ft.ThemeMode.DARK
    page.dark_theme = ft.DarkTheme(
        color_scheme_seed=ACCENT2,
        background_color=BG,
        surface_color=SURFACE,
    )
    page.padding = 0
    page.spacing = 0
    page.window_full_screen = False

    # ── State ────────────────────────────────────────────────────────────
    selected_brand = ft.Ref[Dropdown]()
    serial_input = ft.Ref[TextField]()
    result_display = ft.Ref[Text]()
    result_card = ft.Ref[Container]()
    status_text = ft.Ref[Text]()
    help_text = ft.Ref[Text]()
    db_label = ft.Ref[Text]()
    brand_count_label = ft.Ref[Text]()

    # ── UI Builders ──────────────────────────────────────────────────────
    def make_brand_selector():
        return Dropdown(
            ref=selected_brand,
            label="Select Car Brand",
            hint_text="Choose your radio brand...",
            options=[Option(k) for k in ALGORITHMS.keys()],
            on_change=lambda e: on_brand_change(e),
            bgcolor=SURFACE,
            border_color=BORDER,
            focused_border_color=ACCENT2,
            label_style=ft.TextStyle(color=TEXT_MUTED),
            item_decode=lambda i: i,
        )

    def make_serial_input():
        return TextField(
            ref=serial_input,
            label="Radio Serial Number",
            hint_text="Enter serial number...",
            on_submit=lambda e: calculate(),
            bgcolor=SURFACE,
            border_color=BORDER,
            focused_border_color=ACCENT2,
            label_style=ft.TextStyle(color=TEXT_MUTED),
            text_style=ft.TextStyle(color=TEXT, size=18),
            autofocus=False,
        )

    def make_result_display():
        return Container(
            ref=result_card,
            content=Column([
                Text(
                    "——",
                    ref=result_display,
                    size=48,
                    weight=ft.FontWeight.W_700,
                    font_family="monospace",
                    color=TEXT,
                    text_align=ft.TextAlign.CENTER,
                ),
                Text(
                    "Enter serial and tap Calculate",
                    ref=status_text,
                    size=12,
                    color=TEXT_MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
            padding=30,
            border_radius=16,
            bgcolor=CARD_BG,
            border=ft.border.all(1, BORDER),
            visible=False,
        )

    def make_brand_count_badge():
        return Row([
            Text("🔍", size=14),
            Text(ref=db_label, value=f"{DB_TOTAL}", size=14, weight=ft.FontWeight.W_700, color=GREEN),
            Text(ref=brand_count_label, value=f"free codes across {DB_BRANDS} brands", size=12, color=TEXT_MUTED),
        ], spacing=4, alignment=ft.MainAxisAlignment.CENTER)

    # ── Calculate logic ──────────────────────────────────────────────────
    def calculate():
        brand_key = selected_brand.current.value if selected_brand.current else None
        serial = serial_input.current.value or ""

        if not brand_key:
            page.show_snack_bar(ft.SnackBar(content=Text("Please select a brand first")))
            return

        if not serial.strip():
            page.show_snack_bar(ft.SnackBar(content=Text("Please enter a serial number")))
            return

        algo = ALGORITHMS.get(brand_key)
        if not algo:
            return

        # Try algorithm first
        try:
            is_valid, error = algo.validate_serial(serial)
            if not is_valid:
                result_card.current.visible = True
                result_display.current.value = "???"
                result_display.current.color = RED
                status_text.current.value = f"Invalid serial: {error}"
                status_text.current.color = RED
                result_card.current.update()
                return
        except Exception:
            pass

        try:
            code = algo.calculate(serial.strip())
            result_card.current.visible = True
            result_display.current.value = code
            result_display.current.color = GREEN
            status_text.current.value = f"✅ {brand_key} — Code found!"
            status_text.current.color = GREEN
        except ValueError as e:
            # Try lookup engine
            result_card.current.visible = True
            result_display.current.value = "NOT FOUND"
            result_display.current.color = TEXT_MUTED
            status_text.current.value = str(e)[:100]
            status_text.current.color = TEXT_MUTED

        result_card.current.update()

    def on_brand_change(e):
        brand = selected_brand.current.value if selected_brand.current else None
        if brand and brand in BRAND_HELP:
            help_text.current.value = BRAND_HELP[brand]
        else:
            help_text.current.value = ""
        help_text.current.update()

    def copy_result(e):
        code = result_display.current.value if result_display.current else ""
        if code and code not in ("——", "???", "NOT FOUND"):
            page.set_clipboard(code)
            page.show_snack_bar(ft.SnackBar(content=Text(f"📋 {code} copied!")))

    # ── Build views ──────────────────────────────────────────────────────
    def build_home():
        """Main calculator view."""
        return View(
            "/",
            [
                Container(
                    padding=ft.padding.all(16),
                    expand=True,
                    bgcolor=BG,
                    content=Column(
                        [
                            # Header
                            Row([
                                Text("📻 RadioUnlock", size=22, weight=ft.FontWeight.W_700, color=TEXT),
                                Icon(name=ft.Icons.RADIO, color=ACCENT2),
                            ], spacing=8),
                            Text("Free car radio unlock codes · No ads · No paywalls",
                                 size=12, color=TEXT_MUTED),

                            Container(height=16),

                            # Brand selector
                            make_brand_selector(),
                            Container(height=12),

                            # Serial input
                            make_serial_input(),
                            Container(height=12),

                            # Calculate button
                            ElevatedButton(
                                text="🔓 CALCULATE CODE",
                                on_click=lambda e: calculate(),
                                style=ft.ButtonStyle(
                                    bgcolor=ACCENT,
                                    color=ft.WHITE,
                                    padding=14,
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                ),
                                width=page.width or 400,
                            ),
                            Container(height=16),

                            # Result display
                            make_result_display(),
                            Container(height=8),

                            # Copy button
                            IconButton(
                                icon=ft.Icons.COPY,
                                tooltip="Copy code",
                                on_click=copy_result,
                                icon_color=TEXT_MUTED,
                            ) if result_card.current and result_card.current.visible else Container(),

                            # Help text
                            Text(
                                "",
                                ref=help_text,
                                size=12,
                                color=TEXT_MUTED,
                                italic=True,
                            ),

                            Container(height=8),
                            make_brand_count_badge(),
                            Container(height=8),
                            Text(
                                "💡 Codes not found? Try the EEPROM Reader tab →",
                                size=11, color=TEXT_MUTED, selectable=True,
                            ),
                        ],
                        spacing=0,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ),
            ],
        )

    def build_eeprom():
        """EEPROM reader info view."""
        return View(
            "/eeprom",
            [
                Container(
                    padding=ft.padding.all(16),
                    bgcolor=BG,
                    expand=True,
                    content=Column(
                        [
                            Row([
                                Text("💾 EEPROM Reader", size=22, weight=ft.FontWeight.W_700, color=TEXT),
                            ]),
                            Text("Extract code directly from radio's EEPROM chip",
                                 size=12, color=TEXT_MUTED),
                            Container(height=16),

                            # How it works
                            Container(
                                padding=12,
                                border_radius=12,
                                bgcolor=CARD_BG,
                                border=ft.border.all(1, BORDER),
                                content=Column([
                                    Text("📋 How to get your dump:", size=14, weight=ft.FontWeight.W_600, color=TEXT),
                                    Container(height=8),
                                    Text("1. Remove radio from dashboard", size=13, color=TEXT),
                                    Text("2. Find the 8-pin SOIC chip (24Cxx)", size=13, color=TEXT),
                                    Text("3. Solder to CH341A programmer (~£5)", size=13, color=TEXT),
                                    Text("4. Read with flashrom or CH341A software", size=13, color=TEXT),
                                    Text("5. Save as .bin file", size=13, color=TEXT),
                                ], spacing=4),
                            ),
                            Container(height=12),

                            # Supported chips
                            Container(
                                padding=12,
                                border_radius=12,
                                bgcolor=CARD_BG,
                                border=ft.border.all(1, BORDER),
                                content=Column([
                                    Text("📡 Supported chips:", size=14, weight=ft.FontWeight.W_600, color=TEXT),
                                    Container(height=8),
                                    Text("24C01 · 24C02 · 24C04 · 24C08 · 24C16 · 24C64", size=12, color=TEXT_MUTED),
                                    Container(height=8),
                                    Text("Supported radios:", size=12, weight=ft.FontWeight.W_600, color=TEXT),
                                    Text("Blaupunkt CAR2003/2004/300/CD300", size=12, color=TEXT_MUTED),
                                    Text("Siemens VDO CR500", size=12, color=TEXT_MUTED),
                                    Text("Ford 6000CD / M-Series", size=12, color=TEXT_MUTED),
                                    Text("Bosch Touch & Connect", size=12, color=TEXT_MUTED),
                                    Text("Renault · VW RCD · Nissan Connect", size=12, color=TEXT_MUTED),
                                ], spacing=4),
                            ),
                            Container(height=12),

                            # Buy programmer
                            Container(
                                padding=12,
                                border_radius=12,
                                bgcolor=CARD_BG,
                                border=ft.border.all(1, BORDER),
                                content=Column([
                                    Text("🔧 EEPROM Programmer:", size=14, weight=ft.FontWeight.W_600, color=TEXT),
                                    Container(height=8),
                                    Text("CH341A USB programmer — ~£5 on eBay/Amazon", size=12, color=TEXT),
                                    Text("Works with Windows, macOS, Linux", size=12, color=TEXT),
                                    Text("Use flashrom (free) or CH341A software", size=12, color=TEXT),
                                    Container(height=8),
                                    Text(
                                        "💡 Full chip scan mode finds codes even for unknown radio models",
                                        size=11, color=TEXT_MUTED, italic=True,
                                    ),
                                ], spacing=4),
                            ),

                            Container(height=12),
                            Text(
                                "Note: EEPROM Reader is in the desktop Windows app. "
                                "Mobile app shows this guide.",
                                size=11, color=TEXT_MUTED, italic=True,
                            ),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ),
            ],
        )

    def build_about():
        """About / info view."""
        return View(
            "/about",
            [
                Container(
                    padding=ft.padding.all(16),
                    bgcolor=BG,
                    expand=True,
                    content=Column(
                        [
                            Row([
                                Text("📻 RadioUnlock", size=24, weight=ft.FontWeight.W_700, color=TEXT),
                            ]),
                            Container(height=4),
                            Text("Free car radio unlock codes · No ads · No paywalls",
                                 size=13, color=TEXT_MUTED),
                            Container(height=16),

                            # Stats card
                            Container(
                                padding=16,
                                border_radius=12,
                                bgcolor=ACCENT,
                                content=Row([
                                    Column([
                                        Text(f"{DB_TOTAL}", size=36, weight=ft.FontWeight.W_700, color=ft.WHITE),
                                        Text("Free codes in database", size=12, color=ft.WHITE),
                                    ]),
                                    Container(width=24),
                                    Column([
                                        Text(f"{DB_BRANDS}", size=36, weight=ft.FontWeight.W_700, color=ft.WHITE),
                                        Text("Car brands covered", size=12, color=ft.WHITE),
                                    ]),
                                ], spacing=16),
                            ),
                            Container(height=16),

                            # Working algorithms
                            Container(
                                padding=12,
                                border_radius=12,
                                bgcolor=CARD_BG,
                                border=ft.border.all(1, BORDER),
                                content=Column([
                                    Text("✅ Working Algorithms (instant, no internet):", size=13, weight=ft.FontWeight.W_600, color=GREEN),
                                    Container(height=6),
                                    Text("Ford M-Series · Ford V-Series", size=12, color=TEXT),
                                    Text("Renault / Dacia · Fiat VP1/VP2", size=12, color=TEXT),
                                    Text("VW RCD (lookup) · More coming", size=12, color=TEXT),
                                ], spacing=4),
                            ),
                            Container(height=8),

                            # Supported brands
                            Container(
                                padding=12,
                                border_radius=12,
                                bgcolor=CARD_BG,
                                border=ft.border.all(1, BORDER),
                                content=Column([
                                    Text("🔍 Free Lookup Database:", size=13, weight=ft.FontWeight.W_600, color=ACCENT2),
                                    Container(height=6),
                                    Text(
                                        "Ford · Opel · Vauxhall · Nissan · Land Rover · Renault · "
                                        "Peugeot · Fiat · Alfa · Mercedes · BMW · VW · Audi · Seat · "
                                        "Skoda · Honda · Toyota · Hyundai · Kia · Volvo · and more...",
                                        size=11, color=TEXT_MUTED,
                                    ),
                                ], spacing=4),
                            ),
                            Container(height=16),

                            # Credits
                            Text(
                                "Built for the community. "
                                "Codes have been paywalled for 30 years — not anymore.",
                                size=12, color=TEXT_MUTED, italic=True,
                            ),
                            Container(height=8),
                            Text(
                                "RadioUnlock is free forever. "
                                "If it helped you, share it with someone who needs it.",
                                size=11, color=TEXT_MUTED,
                            ),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ),
            ],
        )

    # ── Navigation ──────────────────────────────────────────────────────
    pages = {
        "/": build_home,
        "/eeprom": build_eeprom,
        "/about": build_about,
    }

    def on_navigation(e: ft.NavigationEvent):
        dest = e.data.get("index", 0)
        routes = ["/", "/eeprom", "/about"]
        route = routes[dest] if dest < len(routes) else "/"
        page.views.clear()
        page.views.append(pages[route]())
        page.update()

    # Initial view
    page.views.append(build_home())
    page.update()

    # Navigation bar (mobile)
    page.navigation_bar = NavigationBar(
        destinations=[
            NavigationDestination(icon=ft.Icons.CALCULATE, label="Calculator"),
            NavigationDestination(icon=ft.Icons.MEMORY, label="EEPROM"),
            NavigationDestination(icon=ft.Icons.INFO_OUTLINE, label="About"),
        ],
        on_change=on_navigation,
        bgcolor=SURFACE,
        indicator_color=ACCENT2,
    )


# ── Entry point ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    ft.app(target=main, app_title="RadioUnlock", view=AppView.WEB_BROWSER)
