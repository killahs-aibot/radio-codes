# -*- coding: utf-8 -*-
"""
LED digit display widget for RadioUnlock.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt


class DigitLabel(QLabel):
    """Individual LED digit box."""
    pass


class CodeDisplay(QWidget):
    """
    LED-style digit display with multiple boxes.

    Displays the unlock code as individual digit boxes styled like
    an LED/LCD display.
    """

    def __init__(self, code_length: int = 4, parent=None):
        super().__init__(parent)
        self._code_length = code_length
        self._digit_labels: list[DigitLabel] = []
        self._current_code: str = ""
        self._setup_ui()

    def _setup_ui(self):
        """Build the digit box layout."""
        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()

        for i in range(self._code_length):
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.NoFrame)
            frame.setStyleSheet(
                "background-color: #0D1117;"
                "border: 1px solid #30363D;"
                "border-radius: 6px;"
                "min-width: 54px;"
                "max-width: 54px;"
                "min-height: 66px;"
                "max-height: 66px;"
            )

            digit = DigitLabel(frame)
            digit.setObjectName("digit_placeholder")
            digit.setText("—")
            digit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            digit.setStyleSheet(
                "background-color: transparent;"
                "color: #30363D;"
                "font-size: 42px;"
                "font-weight: bold;"
                "font-family: 'Courier New', monospace;"
                "border: none;"
            )

            # Center the digit inside the frame using a layout
            frame_layout = QHBoxLayout(frame)
            frame_layout.setContentsMargins(0, 0, 0, 0)
            frame_layout.setSpacing(0)
            frame_layout.addWidget(digit)

            self._digit_labels.append(digit)
            layout.addWidget(frame)

        layout.addStretch()

    def set_code(self, code_str: str) -> None:
        """
        Display a code string in the digit boxes.

        Fills boxes left to right, pads with "—" for missing digits.
        """
        self._current_code = code_str
        padded = code_str.ljust(self._code_length, "—")
        for i, digit_label in enumerate(self._digit_labels):
            char = padded[i] if i < len(padded) else "—"
            digit_label.setText(char)
            digit_label.setObjectName("")
            digit_label.setStyleSheet(
                "background-color: transparent;"
                "color: #58A6FF;"
                "font-size: 42px;"
                "font-weight: bold;"
                "font-family: 'Courier New', monospace;"
                "border: none;"
            )

    def clear(self) -> None:
        """Reset all digit boxes to the empty style."""
        self._current_code = ""
        for digit_label in self._digit_labels:
            digit_label.setText("—")
            digit_label.setObjectName("digit_placeholder")
            digit_label.setStyleSheet(
                "background-color: transparent;"
                "color: #30363D;"
                "font-size: 42px;"
                "font-weight: bold;"
                "font-family: 'Courier New', monospace;"
                "border: none;"
            )

    def animate_success(self) -> None:
        """
        Briefly flash green border to indicate successful code calculation.
        """
        from PySide6.QtCore import QTimer

        # Apply green border style to all digit frames
        for digit_label in self._digit_labels:
            parent = digit_label.parent()
            if parent:
                parent.setStyleSheet(
                    "background-color: #0D1117;"
                    "border: 2px solid #3FB950;"
                    "border-radius: 6px;"
                    "min-width: 54px;"
                    "max-width: 54px;"
                    "min-height: 66px;"
                    "max-height: 66px;"
                )
                digit_label.setStyleSheet(
                    "background-color: transparent;"
                    "color: #3FB950;"
                    "font-size: 42px;"
                    "font-weight: bold;"
                    "font-family: 'Courier New', monospace;"
                    "border: none;"
                )

        # Restore normal style after 1200ms
        QTimer.singleShot(1200, self._restore_normal_style)

    def animate_error(self) -> None:
        """
        Briefly flash red border to indicate an error.
        """
        from PySide6.QtCore import QTimer

        # Apply red border style to all digit frames
        for digit_label in self._digit_labels:
            parent = digit_label.parent()
            if parent:
                parent.setStyleSheet(
                    "background-color: #0D1117;"
                    "border: 2px solid #F85149;"
                    "border-radius: 6px;"
                    "min-width: 54px;"
                    "max-width: 54px;"
                    "min-height: 66px;"
                    "max-height: 66px;"
                )
                digit_label.setStyleSheet(
                    "background-color: transparent;"
                    "color: #F85149;"
                    "font-size: 42px;"
                    "font-weight: bold;"
                    "font-family: 'Courier New', monospace;"
                    "border: none;"
                )

        # Restore normal style after 1200ms
        QTimer.singleShot(1200, self._restore_normal_style)

    def _restore_normal_style(self) -> None:
        """Restore the normal dark style after an animation."""
        for digit_label in self._digit_labels:
            char = digit_label.text()
            if char == "—" or not char:
                digit_label.setObjectName("digit_placeholder")
                digit_label.setStyleSheet(
                    "background-color: transparent;"
                    "color: #30363D;"
                    "font-size: 42px;"
                    "font-weight: bold;"
                    "font-family: 'Courier New', monospace;"
                    "border: none;"
                )
            else:
                digit_label.setObjectName("")
                digit_label.setStyleSheet(
                    "background-color: transparent;"
                    "color: #58A6FF;"
                    "font-size: 42px;"
                    "font-weight: bold;"
                    "font-family: 'Courier New', monospace;"
                    "border: none;"
                )

            parent = digit_label.parent()
            if parent:
                parent.setStyleSheet(
                    "background-color: #0D1117;"
                    "border: 1px solid #30363D;"
                    "border-radius: 6px;"
                    "min-width: 54px;"
                    "max-width: 54px;"
                    "min-height: 66px;"
                    "max-height: 66px;"
                )
