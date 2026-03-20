# -*- coding: utf-8 -*-
"""
Collapsible help panel for RadioUnlock — per-brand serial location instructions.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QToolButton, QTextEdit
)
from PySide6.QtCore import Qt


class HelpPanel(QWidget):
    """
    Collapsible help panel showing how to find serial numbers.

    Content changes based on the selected brand.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_expanded = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toggle button
        self._toggle = QToolButton()
        self._toggle.setObjectName("help_toggle")
        self._toggle.setText("How to find your serial number ▼")
        self._toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._toggle.setArrowType(Qt.ArrowType.DownArrow)
        self._toggle.clicked.connect(self._on_toggle)
        self._toggle.setStyleSheet(
            "QToolButton#help_toggle {"
            "background-color: transparent;"
            "border: none;"
            "color: #58A6FF;"
            "font-size: 13px;"
            "padding: 6px 0px;"
            "text-align: left;"
            "}"
        )

        # Content area
        self._content = QTextEdit()
        self._content.setObjectName("help_content")
        self._content.setReadOnly(True)
        self._content.setMaximumHeight(0)  # Hidden initially
        self._content.setStyleSheet(
            "QTextEdit#help_content {"
            "background-color: #161B22;"
            "border: 1px solid #30363D;"
            "border-radius: 6px;"
            "color: #E6EDF3;"
            "font-size: 13px;"
            "padding: 12px;"
            "}"
        )
        self._content.setHtml(self._default_help_text())

        layout.addWidget(self._toggle)
        layout.addWidget(self._content)

    def _on_toggle(self) -> None:
        """Toggle the help panel expanded/collapsed state."""
        self._is_expanded = not self._is_expanded

        if self._is_expanded:
            self._toggle.setText("How to find your serial number ▲")
            self._toggle.setArrowType(Qt.ArrowType.UpArrow)
            # Animate to full height
            self._content.setMaximumHeight(200)
        else:
            self._toggle.setText("How to find your serial number ▼")
            self._toggle.setArrowType(Qt.ArrowType.DownArrow)
            self._content.setMaximumHeight(0)

    def set_brand_help(self, brand_name: str, hint: str, serial_format: str) -> None:
        """
        Update the help content for a selected brand.

        Args:
            brand_name: Display name of the brand (e.g. "Ford")
            hint: The serial_hint from BrandInfo
            serial_format: Human-readable serial format description
        """
        # Build bullet-pointed help text
        bullet = "📻"
        html = f"""
        <div style="color: #E6EDF3; font-size: 13px; line-height: 1.6;">
        <p style="color: #7D8590; margin-bottom: 8px;">
            <b>Finding the serial for {brand_name}</b>
        </p>
        <p style="margin-bottom: 6px;">{bullet} <b>Option 1 — On the radio label:</b><br/>
        &nbsp;&nbsp;&nbsp;Look for a printed label on the radio casing itself.<br/>
        &nbsp;&nbsp;&nbsp;The serial is usually near a barcode or "S/N" marking.</p>
        <p style="margin-bottom: 6px;">{bullet} <b>Option 2 — On the car display:</b><br/>
        &nbsp;&nbsp;&nbsp;Some radios display the serial on screen when you<br/>
        &nbsp;&nbsp;&nbsp;hold preset buttons 1 & 6 together while the radio is off.</p>
        <p style="margin-bottom: 6px;">{bullet} <b>Option 3 — Vehicle documents:</b><br/>
        &nbsp;&nbsp;&nbsp;Check the owner's manual or service handbook.<br/>
        &nbsp;&nbsp;&nbsp;There may be a radio card with the serial printed.</p>
        <p style="margin-bottom: 4px;">{bullet} <b>Format expected:</b> <code style="color: #58A6FF;">{serial_format}</code></p>
        <p style="color: #7D8590; margin-top: 8px; font-size: 12px;">
            {hint}
        </p>
        </div>
        """
        self._content.setHtml(html)

    def _default_help_text(self) -> str:
        """Default text shown before any brand is selected."""
        return """
        <div style="color: #7D8590; font-size: 13px; line-height: 1.6;">
        <p>Select a brand above to see instructions for finding your serial number.</p>
        </div>
        """

    def collapse(self) -> None:
        """Collapse the panel."""
        if self._is_expanded:
            self._is_expanded = False
            self._toggle.setText("How to find your serial number ▼")
            self._toggle.setArrowType(Qt.ArrowType.DownArrow)
            self._content.setMaximumHeight(0)
