# -*- coding: utf-8 -*-
"""
RadioUnlock — Windows Desktop App (Pure Python + tkinter)
Standalone Windows executable built with PyInstaller. No Flutter required.

This is the launcher for the PyInstaller build. It imports the radiocodes
modules and launches a tkinter GUI. Use PyInstaller to bundle this.

Build on Windows:
  pip install pyinstaller
  pyinstaller --onefile --windowed --name RadioUnlock ^
    --add-data "src;radiocodes" ^
    --hidden-import radiocodes.algorithms ^
    --hidden-import radiocodes.lookup_engine ^
    --hidden-import radiocodes.eeprom_analyzer ^
    --hidden-import radiocodes.serial_detector ^
    --hidden-import radiocodes.bluepill.analyzer ^
    --collect-all flet ^
    windows_launcher.py
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ── Bootstrap ──────────────────────────────────────────────────────────────
# Add src to path so we can import radiocodes
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    bundle_dir = sys._MEIPASS
    src_path = os.path.join(bundle_dir, 'radiocodes')
    sys.path.insert(0, bundle_dir)
else:
    # Running from source
    src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from radiocodes.algorithms import (
    FordMAlgorithm, FordVAlgorithm, RenaultAlgorithm,
    VWRCDAlgorithm, VauxhallAlgorithm, FiatAlgorithm,
    NissanAlgorithm, HondaAlgorithm, KiaAlgorithm,
)
from radiocodes.lookup_engine import load_csv, get_stats
from radiocodes.eeprom_analyzer import analyze as eeprom_analyze, identify_chip, get_supported_models
from radiocodes.serial_detector import detect_brand, get_format_hint

# Load database — use data/ from frozen bundle or source
if getattr(sys, 'frozen', False):
    _data_dir = os.path.join(sys._MEIPASS, 'data')
else:
    _data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
_csv_path = os.path.join(_data_dir, 'forum_pairs.csv')

load_csv(_csv_path)
STATS = get_stats()
DB_TOTAL = STATS["total_pairs"]
DB_BRANDS = len(STATS["brands"])

# ── Colour scheme ─────────────────────────────────────────────────────────
BG = "#0D1117"
SURFACE = "#161B22"
CARD = "#1C2128"
ACCENT = "#238636"
ACCENT2 = "#1F6FEB"
TEXT = "#E6EDF3"
MUTED = "#7D8590"
BORDER = "#30363D"
RED = "#F85149"
GREEN = "#3FB950"
ORANGE = "#D29922"


# ── Algorithm registry ─────────────────────────────────────────────────────
ALGOS = {
    "Ford M-Series": FordMAlgorithm(),
    "Ford V-Series": FordVAlgorithm(),
    "Renault / Dacia": RenaultAlgorithm(),
    "Kia": KiaAlgorithm(),
    "VW / Audi / Seat / Skoda": VWRCDAlgorithm(),
    "Vauxhall / Opel": VauxhallAlgorithm(),
    "Fiat / Alfa Romeo": FiatAlgorithm(),
    "Nissan": NissanAlgorithm(),
    "Honda": HondaAlgorithm(),
    "Acura": HondaAlgorithm(),
}

BRAND_HELP = {
    "Ford M-Series": "Enter serial starting with M (e.g. M025345)",
    "Ford V-Series": "Enter serial starting with V (e.g. V007337)",
    "Renault / Dacia": "Enter pre-code: 1 letter + 3 digits (e.g. D123)",
    "Kia": "Enter serial with letter + 3 digits (e.g. H050, B777)",
    "VW / Audi / Seat / Skoda": "Enter full 14-char serial (e.g. VWZ5Z7B5013069)",
    "Vauxhall / Opel": "Enter serial starting with GM (e.g. GM020328268659)",
    "Fiat / Alfa Romeo": "Enter last 4 digits of serial (e.g. VP1-1234 → enter 1234)",
    "Nissan": "Try serial or use FREE portal: radio-navicode.nissan.com",
    "Honda": "🌐 FREE portal: radio-navicode.honda.com — Enter VIN + radio serial",
    "Acura": "🌐 FREE portal: radio-navicode.acura.com — Same as Honda",
}


# ── App ────────────────────────────────────────────────────────────────────
class RadioUnlockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RadioUnlock")
        self.root.configure(bg=BG)
        self.root.geometry("520x700")
        self.root.minsize(480, 600)

        # Attempt to load icon if present
        try:
            self.root.iconbitmap("icon.ico")
        except Exception:
            pass

        self.selected_brand = None
        self._build_ui()

    def _style(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('BG.TFrame', background=BG)
        style.configure('Surface.TFrame', background=SURFACE)
        style.configure('Card.TFrame', background=CARD)
        style.configure('BG.TLabel', background=BG, foreground=TEXT, font=('Segoe UI', 10))
        style.configure('Title.TLabel', background=BG, foreground=TEXT, font=('Segoe UI', 20, 'bold'))
        style.configure('Muted.TLabel', background=BG, foreground=MUTED, font=('Segoe UI', 9))
        style.configure('Section.TLabel', background=BG, foreground=MUTED, font=('Segoe UI', 10, 'bold'))
        style.configure('Green.TLabel', background=BG, foreground=GREEN, font=('Segoe UI', 11, 'bold'))
        style.configure('Accent.TButton', background=ACCENT, foreground='white')
        style.configure('Card.TButton', background=CARD, foreground=TEXT)

        style.map('Accent.TButton', background=[('active', ACCENT2)])

        style.configure('Brand.TCombobox',
                       fieldbackground=SURFACE, background=SURFACE,
                       foreground=TEXT, bordercolor=BORDER)
        style.configure('Brand.TCombobox', insertcolor=TEXT)

        return style

    def _build_ui(self):
        s = self._style()
        self.root.columnconfigure(0, weight=1)

        # ── Scrollable canvas ────────────────────────────────────────────
        canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0,
                           width=520, height=700)
        scrollbar = ttk.Scrollbar(self.root, orient='vertical', command=canvas.yview)
        scrollable = ttk.Frame(canvas, style='BG.TFrame')

        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Mousewheel on canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        pad = {'padx': 16, 'pady': 8, 'sticky': 'ew'}

        # ── Header ────────────────────────────────────────────────────────
        header = tk.Frame(scrollable, bg=BG)
        header.pack(fill='x', pady=(16, 4))
        ttk.Label(header, text="📻  RadioUnlock", style='Title.TLabel').pack(anchor='w')
        ttk.Label(header, text=f"Free car radio codes · {DB_TOTAL} codes across {DB_BRANDS} brands", style='Muted.TLabel').pack(anchor='w')

        self._card(scrollable, pady=(8, 0), children=[
            lambda p: ttk.Label(p, text="SELECT BRAND", style='Section.TLabel').pack(anchor='w'),
            lambda p: self._brand_grid(p),
        ])

        self._card(scrollable, children=[
            lambda p: ttk.Label(p, text="ENTER SERIAL", style='Section.TLabel').pack(anchor='w'),
            lambda p: ttk.Label(p, text="", name='detect_hint', style='Muted.TLabel').pack(anchor='w'),
            lambda p: self._serial_field(p),
            lambda p: self._calc_btn(p),
        ])

        self.result_frame = self._card(scrollable, visible=False, children=[
            lambda p: ttk.Label(p, text="🔓  YOUR CODE", style='Section.TLabel').pack(anchor='w'),
            lambda p: tk.Label(p, text="", name='result', font=('Consolas', 48, 'bold'),
                              fg=GREEN, bg=CARD).pack(anchor='center', pady=16),
            lambda p: ttk.Label(p, text="", name='status', style='Muted.TLabel').pack(anchor='center'),
            lambda p: tk.Button(p, text="📋  Copy Code", command=self._copy_code,
                              bg=CARD, fg=TEXT, font=('Segoe UI', 11),
                              relief='flat', padx=16, pady=6,
                              cursor='hand2').pack(anchor='center', pady=8),
        ])

        self.eeprom_frame = self._card(scrollable, visible=False, children=[
            lambda p: ttk.Label(p, text="💾  EEPROM ANALYZER", style='Section.TLabel').pack(anchor='w'),
            lambda p: ttk.Label(p, text="Load a .bin dump from your radio's 24Cxx chip", style='Muted.TLabel').pack(anchor='w'),
            lambda p: self._eeprom_ui(p),
        ])

        # ── Bottom nav ────────────────────────────────────────────────────
        nav = tk.Frame(scrollable, bg=SURFACE)
        nav.pack(fill='x', side='bottom', pady=(16, 0))
        for i, (label, cmd) in enumerate([
            ("🔢 Calculator", lambda: self._show_tab('calc')),
            ("💾 EEPROM", lambda: self._show_tab('eeprom')),
            ("ℹ️  About", lambda: self._show_tab('about')),
        ]):
            btn = tk.Button(nav, text=label, command=cmd, bg=SURFACE, fg=TEXT,
                           font=('Segoe UI', 10), relief='flat', cursor='hand2')
            btn.pack(side='left', expand=True, pady=12)

    def _card(self, parent, visible=True, children=None, pady=8, **kwargs):
        """Create a card frame with optional children."""
        frame = tk.Frame(parent, bg=CARD, **kwargs)
        frame.pack(fill='x', pady=pady, padx=16)
        if not visible:
            frame.pack_forget()
        if children:
            for child_fn in children:
                child_fn(frame)
        return frame

    def _brand_grid(self, parent):
        brands = list(ALGOS.keys())
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill='x', pady=4)
        for i, brand in enumerate(brands):
            col = i % 2
            if i > 0 and col == 0:
                row = tk.Frame(parent, bg=CARD)
                row.pack(fill='x', pady=4)
            btn = tk.Button(row, text=brand, command=lambda b=brand: self._select_brand(b),
                           bg=SURFACE, fg=TEXT, font=('Segoe UI', 10),
                           relief='groove', padx=8, pady=6, cursor='hand2',
                           activebackground=ACCENT2, activeforeground='white')
            btn.pack(side='left', expand=True, fill='x', padx=2)

    def _serial_field(self, parent):
        self.serial_var = tk.StringVar()
        self.serial_var.trace_add('write', lambda *_: self._on_serial_change())

        frame = tk.Frame(parent, bg=CARD)
        frame.pack(fill='x', pady=6)
        self.serial_entry = tk.Entry(frame, textvariable=self.serial_var,
                                    font=('Consolas', 16), bg=SURFACE, fg=TEXT,
                                    insertbackground=TEXT, relief='flat', bd=0,
                                    highlightthickness=1, highlightcolor=ACCENT2,
                                    highlightbackground=BORDER)
        self.serial_entry.pack(fill='x', padx=4, pady=4)

    def _calc_btn(self, parent):
        btn = tk.Button(parent, text="🔓  CALCULATE CODE", command=self._calculate,
                       bg=ACCENT, fg='white', font=('Segoe UI', 13, 'bold'),
                       relief='flat', pady=10, cursor='hand2', activebackground=ACCENT2)
        btn.pack(fill='x', pady=(4, 4))

    def _eeprom_ui(self, parent):
        tk.Label(parent, text="Radio Model:", fg=TEXT, bg=CARD,
                font=('Segoe UI', 10)).pack(anchor='w')
        self.eeprom_model = ttk.Combobox(parent, values=['FULL SCAN'] + get_supported_models(),
                                        state='readonly', font=('Segoe UI', 10))
        self.eeprom_model.set('FULL SCAN')
        self.eeprom_model.pack(fill='x', pady=4)

        tk.Button(parent, text="📂  Load EEPROM Dump (.bin)",
                 command=self._load_eeprom,
                 bg=SURFACE, fg=TEXT, font=('Segoe UI', 10),
                 relief='groove', pady=6, cursor='hand2').pack(fill='x', pady=4)

        self.eeprom_result = tk.Label(parent, text="", fg=TEXT, bg=CARD,
                                      font=('Consolas', 10), justify='left', anchor='w')
        self.eeprom_result.pack(fill='x', pady=4)

    def _select_brand(self, brand):
        self.selected_brand = brand
        self.result_frame.pack_forget()
        self.eeprom_frame.pack_forget()
        calc_card = self.result_frame.master
        self.result_frame.pack(fill='x', pady=8, padx=16)
        self.root.update()

        # Help text
        hint = BRAND_HELP.get(brand, "")
        hint_label = self.serial_entry.master.nametowidget('detect_hint') \
            if 'detect_hint' in self.serial_entry.master.children else None
        if hint_label:
            hint_label.configure(text=hint)

        self.serial_entry.focus()

    def _on_serial_change(self):
        serial = self.serial_var.get().strip()
        hint_label = None
        try:
            hint_label = self.serial_entry.master.nametowidget('detect_hint')
        except Exception:
            pass

        if len(serial) >= 3 and hint_label:
            detected, conf = detect_brand(serial)
            if detected and conf >= 0.6:
                hint_label.configure(text=f"🔍 Detected: {detected} ({conf:.0%})", fg=GREEN)
            elif detected:
                hint_label.configure(text=get_format_hint(serial), fg=MUTED)
            else:
                hint_label.configure(text=get_format_hint(serial), fg=MUTED)
        elif hint_label:
            hint_label.configure(text="", fg=MUTED)

    def _calculate(self):
        if not self.selected_brand:
            messagebox.showwarning("⚠️", "Select a brand first")
            return

        serial = self.serial_var.get().strip()
        if not serial:
            messagebox.showwarning("⚠️", "Enter a serial number")
            return

        algo = ALGOS.get(self.selected_brand)
        if not algo:
            return

        valid, err = algo.validate_serial(serial)
        if not valid:
            messagebox.showerror("Invalid Serial", f"Error: {err}")
            return

        try:
            code = algo.calculate(serial)
            result_label = self.result_frame.nametowidget('result')
            status_label = self.result_frame.nametowidget('status')
            result_label.configure(text=code, fg=GREEN)
            status_label.configure(text=f"✅ {self.selected_brand}", fg=GREEN)
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
        except ValueError as e:
            messagebox.showinfo("Code Not Found", str(e))

    def _copy_code(self):
        code = self.root.clipboard_get()
        if code:
            messagebox.showinfo("📋", f"Copied: {code}")

    def _load_eeprom(self):
        path = filedialog.askopenfilename(
            title="Load EEPROM Dump",
            filetypes=[("BIN files", "*.bin"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, 'rb') as f:
                data = f.read()

            model = self.eeprom_model.get()
            chip = identify_chip(data)
            matches = eeprom_analyze(data, model if model in get_supported_models() else "FULL SCAN")

            lines = [f"📦 Chip: {chip}", f"📋 Model: {model}", ""]
            if matches:
                lines.append(f"✅ Found {len(matches)} potential code(s):")
                for m in matches[:10]:
                    conf_emoji = {"high": "🟢", "medium": "🟡", "low": "⚪️"}.get(m.confidence, "⚪️")
                    lines.append(f"  {conf_emoji} 0x{m.address:04X} → {m.code} [{m.confidence}]")
            else:
                lines.append("❌ No codes found. Try FULL SCAN or another model.")

            self.eeprom_result.configure(text="\n".join(lines))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dump:\n{e}")

    def _show_tab(self, tab):
        if tab == 'calc':
            self.result_frame.pack(fill='x', pady=8, padx=16)
            try:
                self.eeprom_frame.pack_forget()
            except Exception:
                pass
        elif tab == 'eeprom':
            self.eeprom_frame.pack(fill='x', pady=8, padx=16)
            try:
                self.result_frame.pack_forget()
            except Exception:
                pass
        elif tab == 'about':
            self.result_frame.pack_forget()
            try:
                self.eeprom_frame.pack_forget()
            except Exception:
                pass
            self._show_about()

    def _show_about(self):
        win = tk.Toplevel(self.root)
        win.title("About RadioUnlock")
        win.configure(bg=BG)
        win.geometry("420x500")

        frame = tk.Frame(win, bg=BG, padx=20, pady=20)
        frame.pack(fill='both', expand=True)

        tk.Label(frame, text="📻  RadioUnlock", font=('Segoe UI', 18, 'bold'),
                fg=TEXT, bg=BG).pack(anchor='w')
        tk.Label(frame, text="Free car radio codes · No ads · No paywalls",
                fg=MUTED, bg=BG).pack(anchor='w')
        tk.Label(frame, text=f"{DB_TOTAL} codes across {DB_BRANDS} brands",
                fg=GREEN, bg=BG, font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(8, 16))

        info = [
            ("✅ Working Algorithms", "Ford M/V · Renault · Kia · Fiat VP1/VP2"),
            ("⚠️  Database Lookup", "VW · Opel/Vauxhall · Nissan · Peugeot"),
            ("🏁  Free Official Portals", "Honda · Acura (radio-navicode.honda.com)"),
            ("💾  EEPROM Analyzer", "Reads 24C01–24C64 dumps for ALL brands"),
        ]
        for title, desc in info:
            tk.Label(frame, text=title, fg=TEXT, bg=BG, font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(8, 0))
            tk.Label(frame, text=desc, fg=MUTED, bg=BG, font=('Segoe UI', 9)).pack(anchor='w')

        tk.Label(frame, text="Built by Killah · Open source · No tracking",
                fg=MUTED, bg=BG, font=('Segoe UI', 8)).pack(side='bottom', pady=10)


def main():
    root = tk.Tk()
    app = RadioUnlockApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
