# -*- coding: utf-8 -*-
"""
Serial number input widget with real-time validation for RadioUnlock.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel
from PySide6.QtCore import Signal, Qt


class SerialInput(QWidget):
    """
    Serial number input field with validation feedback.

    Emits `serial_changed(serial: str)` when text changes.
    """

    serial_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_hint: str = "Format: 6 digits (e.g. 123456)"
        self._current_serial: str = ""
        self._is_valid: bool = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)

        self._input = QLineEdit()
        self._input.setObjectName("serial_input")
        self._input.setPlaceholderText("Enter serial number...")
        self._input.setMinimumHeight(44)
        self._input.setStyleSheet(
            "background-color: #161B22;"
            "border: 1px solid #30363D;"
            "border-radius: 6px;"
            "color: #E6EDF3;"
            "font-size: 20px;"
            "font-family: 'Courier New', monospace;"
            "padding: 10px 12px;"
        )
        self._input.textChanged.connect(self._on_text_changed)
        self._input.returnPressed.connect(self._on_return_pressed)

        self._hint = QLabel(self._current_hint)
        self._hint.setObjectName("hint_label")
        self._hint.setStyleSheet(
            "color: #7D8590;"
            "font-size: 12px;"
        )

        layout.addWidget(self._input)
        layout.addWidget(self._hint)

    def _on_text_changed(self, text: str) -> None:
        """Handle text changes and update border color."""
        self._current_serial = text
        self.serial_changed.emit(text)

        if not text:
            self._set_border_state("neutral")
            return

        # We don't validate here - validation happens on calculate
        # But we can show a tentative style
        self._set_border_state("neutral")

    def _set_border_state(self, state: str) -> None:
        """Update the input border color based on validation state."""
        if state == "valid":
            self._input.setStyleSheet(
                "background-color: #161B22;"
                "border: 1px solid #3FB950;"
                "border-radius: 6px;"
                "color: #E6EDF3;"
                "font-size: 20px;"
                "font-family: 'Courier New', monospace;"
                "padding: 10px 12px;"
            )
        elif state == "invalid":
            self._input.setStyleSheet(
                "background-color: #161B22;"
                "border: 1px solid #F85149;"
                "border-radius: 6px;"
                "color: #E6EDF3;"
                "font-size: 20px;"
                "font-family: 'Courier New', monospace;"
                "padding: 10px 12px;"
            )
        else:
            self._input.setStyleSheet(
                "background-color: #161B22;"
                "border: 1px solid #30363D;"
                "border-radius: 6px;"
                "color: #E6EDF3;"
                "font-size: 20px;"
                "font-family: 'Courier New', monospace;"
                "padding: 10px 12px;"
            )

    def _on_return_pressed(self) -> None:
        """Handle Enter key - emit signal for calculate."""
        # Let parent know Enter was pressed
        pass

    def set_serial_format(self, hint: str) -> None:
        """Update the hint text (called when brand changes)."""
        self._current_hint = hint
        self._hint.setText(hint)

    def text(self) -> str:
        """Return the current serial text."""
        return self._current_serial

    def setText(self, text: str) -> None:
        """Set the serial text programmatically."""
        self._input.setText(text)

    def set_valid_style(self) -> None:
        """Set border to green (valid format)."""
        self._set_border_state("valid")

    def set_invalid_style(self) -> None:
        """Set border to red (invalid format)."""
        self._set_border_state("invalid")

    def set_neutral_style(self) -> None:
        """Set border to default neutral."""
        self._set_border_state("neutral")

    def clear(self) -> None:
        """Clear the input field."""
        self._input.clear()
        self._current_serial = ""
        self._set_border_state("neutral")

    def set_readonly(self, readonly: bool) -> None:
        """Set whether the input is read-only."""
        self._input.setReadOnly(readonly)

    def returnPressed(self):
        """Connect to returnPressed signal."""
        return self._input.returnPressed
