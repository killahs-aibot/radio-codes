# -*- coding: utf-8 -*-
"""
EEPROM Reader panel for RadioUnlock GUI.
Loads an EEPROM binary dump and extracts the radio unlock code.

User flow:
1. Select radio model (or auto-detect)
2. Load the .bin/.eep/.rom dump file
3. Click "Analyze" → shows potential codes at known addresses
4. Also shows full chip scan for manual review
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTextEdit, QFileDialog,
    QMessageBox, QGroupBox, QScrollArea, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from radiocodes.eeprom_analyzer import (
    analyze_dump, get_supported_models, identify_chip,
    load_dump, CODE_LOCATIONS
)


class EEPROMPanel(QWidget):
    """
    EEPROM dump analyzer panel.
    Allows user to load a binary dump and extract the radio code.
    """

    # Signal when a code is found
    code_found = Signal(str, str)  # (code, model)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dump_data = None
        self._dump_path = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Title
        title = QLabel("💾 EEPROM Code Reader")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        subtitle = QLabel(
            "Load a radio EEPROM dump (.bin, .eep, .rom) and extract the unlock code.\n"
            "Supported chips: 24C01, 24C02, 24C04, 24C08, 24C16, 24C64"
        )
        subtitle.setStyleSheet("color: #7D8590; font-size: 12px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # File selection
        file_group = QGroupBox("📂 Load EEPROM Dump")
        file_layout = QHBoxLayout(file_group)

        self._file_label = QLabel("No file loaded")
        self._file_label.setStyleSheet("color: #7D8590; font-style: italic;")
        self._file_label.setWordWrap(True)
        file_layout.addWidget(self._file_label, 1)

        load_btn = QPushButton("📁 Load Dump File...")
        load_btn.clicked.connect(self._load_file)
        file_layout.addWidget(load_btn)
        layout.addWidget(file_group)

        # Chip info
        self._chip_label = QLabel("Chip: Not loaded")
        self._chip_label.setStyleSheet("color: #58A6FF; font-size: 12px;")
        layout.addWidget(self._chip_label)

        # Radio model selection
        model_group = QGroupBox("📻 Radio Model")
        model_layout = QVBoxLayout(model_group)

        model_layout.addWidget(QLabel(
            "Select your radio model for accurate code extraction.\n"
            "Select 'Generic (4-digit BCD)' to scan all known locations."
        ))

        model_hbox = QHBoxLayout()
        model_hbox.addWidget(QLabel("Model:"))

        self._model_combo = QComboBox()
        self._model_combo.addItems(get_supported_models())
        # Default to Generic
        idx = self._model_combo.findText("Generic (4-digit BCD)")
        if idx >= 0:
            self._model_combo.setCurrentIndex(idx)
        model_hbox.addWidget(self._model_combo, 1)
        model_layout.addLayout(model_hbox)
        layout.addWidget(model_group)

        # Analyze button
        self._analyze_btn = QPushButton("🔍 Analyze Dump")
        self._analyze_btn.setEnabled(False)
        self._analyze_btn.clicked.connect(self._analyze)
        self._analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #238636;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #484F58;
                color: #6E7681;
            }
            QPushButton:hover:enabled {
                background-color: #2EA043;
            }
        """)
        layout.addWidget(self._analyze_btn)

        # Results
        results_group = QGroupBox("📊 Results")
        results_layout = QVBoxLayout(results_group)

        self._results_text = QTextEdit()
        self._results_text.setReadOnly(True)
        self._results_text.setMaximumHeight(200)
        self._results_text.setPlaceholderText(
            "Code results will appear here after analysis.\n\n"
            "🟢 High confidence = very likely correct code\n"
            "🟡 Medium confidence = possible code, verify manually\n"
            "⚪️ Low confidence = found 4 BCD digits, may not be the code"
        )
        self._results_text.setStyleSheet("""
            QTextEdit {
                background-color: #161B22;
                color: #C9D1D9;
                border: 1px solid #30363D;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        results_layout.addWidget(self._results_text)
        layout.addWidget(results_group)

        # Full chip scan button
        self._scan_btn = QPushButton("🔎 Full Chip Scan (All Addresses)")
        self._scan_btn.setEnabled(False)
        self._scan_btn.clicked.connect(self._full_scan)
        layout.addWidget(self._scan_btn)

        # Instructions
        instructions = QLabel(
            "<b>📖 How to get the EEPROM dump:</b><br><br>"
            "1. Remove the radio from your car<br>"
            "2. Locate the 8-pin SOIC chip (usually marked 24Cxx)<br>"
            "3. Solder it to a <b>CH341A programmer</b> (~£5 on eBay)<br>"
            "4. Use <b>flashrom</b> or the CH341A software to read the chip<br>"
            "5. Save as .bin and load it here<br><br>"
            "<b>💡 Tip:</b> If 'Generic Scan' finds codes but your model doesn't, "
            "the code may be stored at a non-standard address. Try multiple models."
        )
        instructions.setStyleSheet("color: #8B949E; font-size: 11px;")
        instructions.setWordWrap(True)
        instructions.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #161B22;
                color: #8B949E;
                border: 1px solid #30363D;
                border-radius: 6px;
                padding: 12px;
                font-size: 11px;
            }
        """)
        layout.addWidget(instructions)

        layout.addStretch()

    def _load_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load EEPROM Dump",
            "",
            "EEPROM Dumps (*.bin *.eep *.rom *.dump *.img);;All Files (*)"
        )
        if not path:
            return

        try:
            self._dump_data = load_dump(path)
            self._dump_path = path
            chip = identify_chip(self._dump_data)
            filename = os.path.basename(path)

            self._file_label.setText(filename)
            self._file_label.setStyleSheet("color: #58A6FF; font-weight: bold;")
            self._chip_label.setText(f"Chip: {chip} | Size: {len(self._dump_data):,} bytes")

            self._analyze_btn.setEnabled(True)
            self._scan_btn.setEnabled(True)
            self._results_text.setPlainText("")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{e}")

    def _analyze(self):
        if not self._dump_data:
            return

        model = self._model_combo.currentText()
        results = analyze_dump(self._dump_data, model)

        if results:
            lines = [f"✅ Found {len(results)} potential code(s):\n"]
            for m in results:
                emoji = {"high": "🟢", "medium": "🟡", "low": "⚪️"}.get(m.confidence, "⚪️")
                lines.append(f"{emoji} Address 0x{m.address:04X} → <b>Code: {m.code}</b>")
                lines.append(f"   Confidence: {m.confidence} | Radio: {m.chip_name}\n")

            text = "\n".join(lines)
            self._results_text.setHtml(text.replace("\n", "<br>"))

            # Emit the best match
            best = results[0]
            self.code_found.emit(best.code, best.chip_name)
        else:
            self._results_text.setHtml(
                "❌ No codes found for this model.<br><br>"
                "Try: <b>Full Chip Scan</b> to search all addresses, "
                "or try a different radio model."
            )

    def _full_scan(self):
        if not self._dump_data:
            return

        results = analyze_dump(self._dump_data, "Generic (4-digit BCD)")

        if results:
            lines = [f"🔎 Full scan found {len(results)} potential code(s):\n"]
            shown = 0
            for m in results:
                if shown >= 20:  # Limit to 20 results
                    lines.append(f"\n...and {len(results) - shown} more (chip may contain non-code data)")
                    break
                emoji = {"high": "🟢", "medium": "🟡", "low": "⚪️"}.get(m.confidence, "⚪️")
                lines.append(f"{emoji} 0x{m.address:04X} → {m.code}  ({m.confidence})")
                shown += 1

            self._results_text.setPlainText("\n".join(lines))
        else:
            self._results_text.setPlainText(
                "❌ Full scan found no valid 4-digit BCD sequences.\n\n"
                "This could mean:\n"
                "  - Wrong EEPROM chip read\n"
                "  - Code is encrypted or stored differently\n"
                "  - Dump is corrupted\n\n"
                "Try checking the chip model and re-reading."
            )
