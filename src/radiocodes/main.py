# -*- coding: utf-8 -*-
"""
RadioUnlock — Free Car Radio Code Calculator.

Entry point for the GUI application.
"""

import sys


def main():
    from PySide6.QtWidgets import QApplication
    from radiocodes.gui import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("RadioUnlock")
    app.setApplicationDisplayName("RadioUnlock")
    app.setOrganizationName("RadioUnlock")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
