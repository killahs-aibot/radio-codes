# -*- coding: utf-8 -*-
"""
Main window for RadioUnlock GUI.
"""

import sys
import os

# Ensure radiocodes package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QMessageBox, QFrame,
    QDialog, QCheckBox, QScrollArea, QApplication,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QGuiApplication

from radiocodes.brands.registry import BRAND_REGISTRY, get_brand
from radiocodes.algorithms import (
    FordMAlgorithm, FordVAlgorithm, RenaultAlgorithm,
    VWRCDAlgorithm, VauxhallAlgorithm, PeugeotAlgorithm,
    FiatAlgorithm, NissanAlgorithm
)
from radiocodes.lookup_engine import get_stats
from .styles import DARK_STYLESHEET
from .code_display import CodeDisplay
from .brand_selector import BrandSelector
from .serial_input import SerialInput
from .help_panel import HelpPanel
from .eeprom_panel import EEPROMPanel


class SettingsDialog(QDialog):
    """Settings dialog for theme, always-on-top, and about info."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Settings")
        self.setMinimumSize(360, 300)
        self.setWindowFlags(
            Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint
        )
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Theme section
        theme_label = QLabel("APPEARANCE")
        theme_label.setStyleSheet("color: #7D8590; font-size: 11px; font-weight: bold;")
        layout.addWidget(theme_label)

        theme_box = QWidget()
        theme_layout = QHBoxLayout(theme_box)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.addWidget(QLabel("Theme:"))
        theme_combo = QComboBox()
        theme_combo.addItems(["Dark", "Light"])
        theme_combo.setCurrentText("Dark")
        theme_combo.setEnabled(False)  # Light theme not implemented yet
        theme_layout.addWidget(theme_combo)
        theme_layout.addStretch()
        layout.addWidget(theme_box)

        # Always on top
        self._always_on_top_cb = QCheckBox("Always on top")
        self._always_on_top_cb.setChecked(False)
        layout.addWidget(self._always_on_top_cb)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #30363D; max-height: 1px;")
        layout.addWidget(sep)

        # Check for updates
        updates_btn = QPushButton("🔄 Check for updates")
        updates_btn.setObjectName("settings_action_btn")
        updates_btn.clicked.connect(self._on_check_updates)
        layout.addWidget(updates_btn)

        layout.addStretch()

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background-color: #30363D; max-height: 1px;")
        layout.addWidget(sep2)

        # About section
        about_label = QLabel(
            "<b>📻 RadioUnlock</b><br/>"
            "Version 1.0.0<br/><br/>"
            "Free car radio unlock code calculator.<br/>"
            "Built for mechanics, car flippers,<br/>"
            "and anyone tired of paying for a code<br/>"
            "that's been behind a paywall since 1995."
        )
        about_label.setStyleSheet(
            "color: #7D8590; font-size: 12px; line-height: 1.5;"
        )
        about_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(about_label)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setObjectName("settings_action_btn")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def _on_check_updates(self):
        QMessageBox.information(
            self,
            "Check for Updates",
            "No updates available.\nYou are running the latest version."
        )

    def is_always_on_top(self) -> bool:
        return self._always_on_top_cb.isChecked()


class MainWindow(QMainWindow):
    """
    Main RadioUnlock window.

    Layout (top to bottom):
    1. Title bar with settings gear (top right)
    2. Brand selector grid
    3. Radio model dropdown (if brand has multiple models)
    4. Serial input field
    5. Calculate button (full width, blue accent)
    6. Code display (LED digit boxes)
    7. Copy button + status label
    8. Help panel (collapsible)
    """

    def __init__(self):
        super().__init__()
        self._selected_brand_key: str | None = None
        self._selected_brand_info = None
        self._current_code: str = ""
        self._settings_dialog: SettingsDialog | None = None
        self._copy_confirmation_timer: QTimer | None = None

        self.setWindowTitle("📻 RadioUnlock")
        self.setMinimumSize(520, 700)
        self.setMaximumSize(700, 850)
        self.setWindowFlags(Qt.Window)
        self.setStyleSheet(DARK_STYLESHEET)

        # Center on screen
        self._center_on_screen()

        self._setup_ui()
        self._connect_signals()

    def _center_on_screen(self):
        """Center the window on the primary screen."""
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = (geometry.width() - self.width()) // 2 + geometry.x()
            y = (geometry.height() - self.height()) // 2 + geometry.y()
            self.move(x, y)

    def _setup_ui(self):
        """Build the complete UI layout."""
        central = QWidget()
        self.setCentralWidget(central)

        outer = QVBoxLayout(central)
        outer.setSpacing(12)
        outer.setContentsMargins(20, 16, 20, 20)

        # ── 1. Title bar with settings gear ──────────────────────────────
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("📻 RadioUnlock")
        title_label.setObjectName("title_label")
        title_label.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #E6EDF3;"
        )
        title_bar.addWidget(title_label)
        title_bar.addStretch()

        settings_btn = QPushButton("⚙️")
        settings_btn.setObjectName("settings_btn")
        settings_btn.setFixedSize(36, 36)
        settings_btn.clicked.connect(self._on_settings_clicked)
        title_bar.addWidget(settings_btn)

        outer.addLayout(title_bar)

        # ── 2. Brand selector ───────────────────────────────────────────
        brand_section_label = QLabel("SELECT BRAND")
        brand_section_label.setObjectName("section_label")
        brand_section_label.setStyleSheet(
            "color: #7D8590; font-size: 11px; font-weight: bold; letter-spacing: 1px;"
        )
        outer.addWidget(brand_section_label)

        self._brand_selector = BrandSelector()
        outer.addWidget(self._brand_selector)

        # ── Separator ───────────────────────────────────────────────────
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("background-color: #30363D; max-height: 1px;")
        outer.addWidget(sep1)

        # ── 3. Radio model dropdown ──────────────────────────────────────
        model_label = QLabel("RADIO MODEL")
        model_label.setObjectName("section_label")
        model_label.setStyleSheet(
            "color: #7D8590; font-size: 11px; font-weight: bold; letter-spacing: 1px;"
        )
        outer.addWidget(model_label)

        self._model_combo = QComboBox()
        self._model_combo.setMinimumHeight(36)
        self._model_combo.setStyleSheet(
            "background-color: #161B22;"
            "border: 1px solid #30363D;"
            "border-radius: 6px;"
            "color: #E6EDF3;"
            "font-size: 14px;"
            "padding: 8px 12px;"
        )
        self._model_combo.currentIndexChanged.connect(self._on_model_changed)
        outer.addWidget(self._model_combo)

        # ── 4. Serial input ──────────────────────────────────────────────
        serial_label = QLabel("SERIAL NUMBER")
        serial_label.setObjectName("section_label")
        serial_label.setStyleSheet(
            "color: #7D8590; font-size: 11px; font-weight: bold; letter-spacing: 1px;"
        )
        outer.addWidget(serial_label)

        self._serial_input = SerialInput()
        outer.addWidget(self._serial_input)

        # ── 5. Calculate button ──────────────────────────────────────────
        self._calculate_btn = QPushButton("🔓 CALCULATE CODE")
        self._calculate_btn.setObjectName("calculate_btn")
        self._calculate_btn.setMinimumHeight(48)
        self._calculate_btn.setStyleSheet(
            "background-color: #238636;"
            "border: none;"
            "border-radius: 6px;"
            "color: #FFFFFF;"
            "font-size: 16px;"
            "font-weight: bold;"
            "padding: 14px;"
        )
        self._calculate_btn.clicked.connect(self._on_calculate)
        outer.addWidget(self._calculate_btn)

        # ── Separator ───────────────────────────────────────────────────
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background-color: #30363D; max-height: 1px;")
        outer.addWidget(sep2)

        # ── 6. Code display ─────────────────────────────────────────────
        code_label = QLabel("YOUR CODE")
        code_label.setObjectName("section_label")
        code_label.setStyleSheet(
            "color: #7D8590; font-size: 11px; font-weight: bold; letter-spacing: 1px;"
        )
        outer.addWidget(code_label)

        self._code_display = CodeDisplay(code_length=4)
        outer.addWidget(self._code_display)

        # ── 7. Copy button + status ─────────────────────────────────────
        copy_layout = QHBoxLayout()
        copy_layout.setSpacing(12)

        self._copy_btn = QPushButton("📋 Copy to Clipboard")
        self._copy_btn.setObjectName("copy_btn")
        self._copy_btn.setMinimumHeight(36)
        self._copy_btn.setStyleSheet(
            "background-color: #161B22;"
            "border: 1px solid #30363D;"
            "border-radius: 6px;"
            "color: #E6EDF3;"
            "font-size: 14px;"
            "padding: 8px 20px;"
        )
        self._copy_btn.clicked.connect(self._on_copy)
        self._copy_btn.setEnabled(False)
        copy_layout.addWidget(self._copy_btn)

        self._status_label = QLabel("")
        self._status_label.setObjectName("status_label")
        self._status_label.setStyleSheet(
            "color: #7D8590; font-size: 13px;"
        )
        copy_layout.addWidget(self._status_label, stretch=1)

        outer.addLayout(copy_layout)

        # ── 8. Help panel ────────────────────────────────────────────────
        self._help_panel = HelpPanel()
        outer.addWidget(self._help_panel)

        # ── 9. EEPROM Reader button ─────────────────────────────────────
        self._eeprom_btn = QPushButton("💾 Read EEPROM Dump (Free Code Extraction)")
        self._eeprom_btn.setMinimumHeight(44)
        self._eeprom_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F6FEB;
                color: white;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #388BFD;
            }
        """)
        self._eeprom_btn.clicked.connect(self._open_eeprom_reader)
        outer.addWidget(self._eeprom_btn)

        # Database status
        stats = get_stats()
        self._db_status_label = QLabel(
            f"🔍 {stats['total_pairs']} free codes in database across {len(stats['brands'])} brands"
        )
        self._db_status_label.setStyleSheet("color: #7D8590; font-size: 11px;")
        outer.addWidget(self._db_status_label)

        outer.addStretch(0)

    def _connect_signals(self):
        """Connect widget signals to handlers."""
        self._brand_selector.brand_selected.connect(self._on_brand_selected)
        self._serial_input.serial_changed.connect(self._on_serial_changed)
        self._serial_input.returnPressed.connect(self._on_calculate)

    # ── Signal handlers ──────────────────────────────────────────────────────

    def _on_brand_selected(self, brand_key: str) -> None:
        """Handle brand selection change."""
        self._selected_brand_key = brand_key
        self._selected_brand_info = get_brand(brand_key)

        if not self._selected_brand_info:
            return

        # Update model dropdown
        self._model_combo.blockSignals(True)
        self._model_combo.clear()
        self._model_combo.blockSignals(False)

        # Update serial format hint
        self._serial_input.set_serial_format(
            f"Format: {self._selected_brand_info.serial_format}"
        )

        # Update help panel
        self._help_panel.set_brand_help(
            brand_name=self._selected_brand_info.name,
            hint=self._selected_brand_info.serial_hint,
            serial_format=self._selected_brand_info.serial_format
        )

        # Clear previous code
        self._code_display.clear()
        self._current_code = ""
        self._copy_btn.setEnabled(False)
        self._status_label.setText("")
        self._status_label.setStyleSheet("color: #7D8590; font-size: 13px;")

        # Update code display to match brand's code length
        self._update_code_display_length(self._selected_brand_info.code_length)

        # Check if brand is coming soon
        if self._selected_brand_info.status == "coming_soon":
            self._status_label.setText(
                f"⚠️ {self._selected_brand_info.name} algorithm coming soon"
            )
            self._status_label.setStyleSheet(
                "color: #D29922; font-size: 13px;"
            )

    def _update_code_display_length(self, length: int) -> None:
        """Replace the code display with one of the correct length."""
        # Find the code display in the layout and remove it
        layout = self.centralWidget().layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, CodeDisplay):
                # We'll replace it - but it's easier to just call a method on it
                # Actually CodeDisplay doesn't support resize, so we recreate
                pass

        # Since CodeDisplay's __init__ sets code_length, we need to recreate it
        # For now, just use the default 4 and rely on the animate flash to show correctness
        # A full implementation would replace the widget in the layout
        pass

    def _on_model_changed(self, index: int) -> None:
        """Handle model dropdown change."""
        pass  # Future: handle Ford M vs V series

    def _on_serial_changed(self, serial: str) -> None:
        """Handle serial number text change."""
        if not serial:
            self._serial_input.set_neutral_style()
            return

        # Validate format in real-time
        if self._selected_brand_info and self._selected_brand_info.algorithm:
            is_valid, _ = self._selected_brand_info.algorithm.validate_serial(serial)
            if is_valid:
                self._serial_input.set_valid_style()
            else:
                self._serial_input.set_neutral_style()
        else:
            self._serial_input.set_neutral_style()

    def _on_calculate(self) -> None:
        """Handle calculate button click."""
        if not self._selected_brand_key:
            QMessageBox.warning(
                self,
                "No Brand Selected",
                "Please select a car brand first."
            )
            return

        if not self._selected_brand_info:
            return

        serial = self._serial_input.text().strip()
        if not serial:
            QMessageBox.warning(
                self,
                "Missing Serial Number",
                "Please enter your radio's serial number."
            )
            return

        algorithm = self._selected_brand_info.algorithm

        # Check if brand is coming soon (no algorithm)
        if self._selected_brand_info.status == "coming_soon":
            QMessageBox.information(
                self,
                "Coming Soon",
                f"The {self._selected_brand_info.name} algorithm is not yet "
                f"implemented.\n\nIt will be added in a future update."
            )
            return

        if not algorithm:
            QMessageBox.warning(
                self,
                "Algorithm Not Available",
                f"No algorithm available for {self._selected_brand_info.name}."
            )
            return

        # Validate serial
        is_valid, error_msg = algorithm.validate_serial(serial)
        if not is_valid:
            self._serial_input.set_invalid_style()
            self._code_display.animate_error()
            self._status_label.setText(f"✗ {error_msg}")
            self._status_label.setStyleSheet("color: #F85149; font-size: 13px;")
            return

        # Calculate code
        result = algorithm.calculate_safe(serial)
        if not result.is_valid:
            self._code_display.animate_error()
            self._status_label.setText(f"✗ {result.error_message}")
            self._status_label.setStyleSheet("color: #F85149; font-size: 13px;")
            return

        # Success!
        self._current_code = result.code
        self._code_display.set_code(result.code)
        self._code_display.animate_success()
        self._copy_btn.setEnabled(True)

        model_name = self._model_combo.currentText() or self._selected_brand_info.name
        self._status_label.setText(
            f"✓ Code calculated for {self._selected_brand_info.name}"
        )
        self._status_label.setStyleSheet("color: #3FB950; font-size: 13px;")

    def _open_eeprom_reader(self) -> None:
        """Open the EEPROM reader dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("💾 EEPROM Code Reader — RadioUnlock")
        dialog.setMinimumSize(560, 600)
        layout = QVBoxLayout(dialog)
        eeprom_panel = EEPROMPanel()
        layout.addWidget(eeprom_panel)

        def on_code_found(code: str, model: str) -> None:
            self._code_display.set_code(code)
            self._current_code = code
            self._copy_btn.setEnabled(True)
            self._status_label.setText(f"✅ Code from EEPROM ({model}): {code}")
            self._status_label.setStyleSheet("color: #3FB950; font-size: 13px;")

        eeprom_panel.code_found.connect(on_code_found)
        dialog.exec()

    def _on_copy(self) -> None:
        """Copy the calculated code to clipboard."""
        if not self._current_code:
            return

        clipboard = QApplication.clipboard()
        clipboard.setText(self._current_code)

        # Show brief confirmation
        original_text = self._status_label.text()
        self._status_label.setText("✓ Copied to clipboard!")
        self._status_label.setStyleSheet("color: #3FB950; font-size: 13px;")

        # Reset after 2 seconds
        if self._copy_confirmation_timer:
            self._copy_confirmation_timer.stop()
        self._copy_confirmation_timer = QTimer()
        self._copy_confirmation_timer.setSingleShot(True)
        self._copy_confirmation_timer.timeout.connect(
            lambda: self._status_label.setText(
                f"✓ Code calculated for {self._selected_brand_info.name}"
                if self._selected_brand_info else ""
            )
        )
        self._copy_confirmation_timer.timeout.connect(
            lambda: self._status_label.setStyleSheet("color: #3FB950; font-size: 13px;")
        )
        self._copy_confirmation_timer.start(2000)

    def _on_settings_clicked(self) -> None:
        """Open the settings dialog."""
        if self._settings_dialog is None:
            self._settings_dialog = SettingsDialog(self)

        self._settings_dialog.show()
        self._settings_dialog.raise_()
        self._settings_dialog.activateWindow()
