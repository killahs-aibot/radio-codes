# -*- coding: utf-8 -*-
"""
Dark theme stylesheet for RadioUnlock GUI.
"""

DARK_STYLESHEET = """
QMainWindow {
    background-color: #0D1117;
    color: #E6EDF3;
}

QWidget {
    background-color: #0D1117;
    color: #E6EDF3;
    font-family: "Segoe UI", sans-serif;
}

QLabel {
    background-color: transparent;
    color: #E6EDF3;
    border: none;
}

QLabel#title_label {
    font-size: 22px;
    font-weight: bold;
    color: #E6EDF3;
}

QLabel#section_label {
    font-size: 12px;
    font-weight: bold;
    color: #7D8590;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QLabel#hint_label {
    font-size: 12px;
    color: #7D8590;
}

QLabel#status_label {
    font-size: 13px;
    color: #7D8590;
}

QLabel#success_status {
    font-size: 13px;
    color: #3FB950;
}

QLabel#error_status {
    font-size: 13px;
    color: #F85149;
}

QLabel#about_label {
    font-size: 12px;
    color: #7D8590;
    padding: 4px;
}

/* Digit box for LED display */
QDigiLabel {
    background-color: #0D1117;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #58A6FF;
    font-size: 42px;
    font-weight: bold;
    font-family: "Courier New", monospace;
    qproperty-alignment: AlignCenter;
    min-width: 54px;
    max-width: 54px;
    min-height: 66px;
    max-height: 66px;
}

QDigiLabel#digit_placeholder {
    color: #30363D;
}

/* Brand button */
QBrandButton {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #E6EDF3;
    font-size: 11px;
    padding: 8px 4px;
    min-width: 100px;
    max-width: 100px;
    min-height: 80px;
    max-height: 80px;
}

QBrandButton:hover {
    background-color: #21262D;
    border-color: #58A6FF;
}

QBrandButton#selected {
    background-color: #1C2128;
    border: 2px solid #58A6FF;
}

QBrandButton#coming_soon {
    background-color: #161B22;
    opacity: 0.5;
}

/* Serial input */
QLineEdit#serial_input {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #E6EDF3;
    font-size: 20px;
    font-family: "Courier New", monospace;
    padding: 10px 12px;
    min-height: 36px;
}

QLineEdit#serial_input:focus {
    border-color: #58A6FF;
}

QLineEdit#serial_input#valid {
    border-color: #3FB950;
}

QLineEdit#serial_input#invalid {
    border-color: #F85149;
}

/* Calculate button */
QPushButton#calculate_btn {
    background-color: #238636;
    border: none;
    border-radius: 6px;
    color: #FFFFFF;
    font-size: 16px;
    font-weight: bold;
    padding: 14px;
    min-height: 36px;
}

QPushButton#calculate_btn:hover {
    background-color: #2EA043;
}

QPushButton#calculate_btn:pressed {
    background-color: #238636;
}

QPushButton#calculate_btn:disabled {
    background-color: #21262D;
    color: #7D8590;
}

/* Copy button */
QPushButton#copy_btn {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #E6EDF3;
    font-size: 14px;
    padding: 8px 20px;
    min-height: 32px;
}

QPushButton#copy_btn:hover {
    border-color: #58A6FF;
    color: #58A6FF;
}

/* Settings gear button */
QPushButton#settings_btn {
    background-color: transparent;
    border: none;
    color: #7D8590;
    font-size: 18px;
    padding: 4px;
    min-width: 32px;
    max-width: 32px;
}

QPushButton#settings_btn:hover {
    color: #E6EDF3;
}

/* Model dropdown */
QComboBox {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #E6EDF3;
    font-size: 14px;
    padding: 8px 12px;
    min-height: 28px;
}

QComboBox:hover {
    border-color: #58A6FF;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #7D8590;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #E6EDF3;
    selection-background-color: #21262D;
    selection-color: #E6EDF3;
}

/* Help toggle button */
QToolButton#help_toggle {
    background-color: transparent;
    border: none;
    color: #58A6FF;
    font-size: 13px;
    padding: 6px 0px;
    text-align: left;
}

QToolButton#help_toggle:hover {
    color: #79C0FF;
}

/* Help content area */
QTextEdit#help_content {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #E6EDF3;
    font-size: 13px;
    padding: 12px;
}

/* Separator */
QFrame#separator {
    background-color: #30363D;
    max-height: 1px;
}

/* Settings dialog */
QDialog {
    background-color: #0D1117;
    color: #E6EDF3;
}

QCheckBox {
    background-color: transparent;
    color: #E6EDF3;
    font-size: 14px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #30363D;
    background-color: #161B22;
}

QCheckBox::indicator:checked {
    background-color: #238636;
    border-color: #238636;
}

QPushButton#settings_action_btn {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #E6EDF3;
    font-size: 13px;
    padding: 8px 16px;
    min-height: 28px;
}

QPushButton#settings_action_btn:hover {
    border-color: #58A6FF;
}

/* Scroll area */
QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollBar:vertical {
    background-color: #0D1117;
    width: 6px;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background-color: #30363D;
    border-radius: 3px;
    min-height: 30px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #0D1117;
    height: 6px;
    border-radius: 3px;
}

QScrollBar::handle:horizontal {
    background-color: #30363D;
    border-radius: 3px;
    min-width: 30px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""
