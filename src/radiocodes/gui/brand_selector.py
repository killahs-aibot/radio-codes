# -*- coding: utf-8 -*-
"""
Brand selection grid widget for RadioUnlock.
"""

from PySide6.QtWidgets import (
    QWidget, QGridLayout, QPushButton, QScrollArea, QVBoxLayout
)
from PySide6.QtCore import Signal, Qt

from radiocodes.brands.registry import BRAND_REGISTRY, BrandInfo


class BrandButton(QPushButton):
    """Individual brand selection button."""

    def __init__(self, brand_key: str, brand_info: BrandInfo, parent=None):
        super().__init__(parent)
        self._brand_key = brand_key
        self._brand_info = brand_info
        self._is_selected = False
        self._setup_ui()

    def _setup_ui(self):
        is_working = brand_info.status == "working"
        is_coming = brand_info.status == "coming_soon"

        # Status dot: green for working, grey for coming soon
        dot = "🟢" if is_working else "⚪"

        self.setText(f"{brand_info.icon}\n{brand_info.name}\n{dot}")
        self.setMinimumSize(100, 80)
        self.setMaximumSize(100, 80)
        self.setStyleSheet(
            "background-color: #161B22;"
            "border: 1px solid #30363D;"
            "border-radius: 6px;"
            "color: #E6EDF3;"
            "font-size: 11px;"
            "padding: 6px 4px;"
            "text-align: center;"
        )

        if is_coming:
            self.setStyleSheet(
                "background-color: #161B22;"
                "border: 1px solid #30363D;"
                "border-radius: 6px;"
                "color: #E6EDF3;"
                "font-size: 11px;"
                "padding: 6px 4px;"
                "text-align: center;"
                "opacity: 0.5;"
            )

    def set_selected(self, selected: bool) -> None:
        """Update visual state for selection."""
        self._is_selected = selected
        if selected:
            self.setStyleSheet(
                "background-color: #1C2128;"
                "border: 2px solid #58A6FF;"
                "border-radius: 6px;"
                "color: #E6EDF3;"
                "font-size: 11px;"
                "padding: 6px 4px;"
                "text-align: center;"
            )
        else:
            is_coming = self._brand_info.status == "coming_soon"
            if is_coming:
                self.setStyleSheet(
                    "background-color: #161B22;"
                    "border: 1px solid #30363D;"
                    "border-radius: 6px;"
                    "color: #E6EDF3;"
                    "font-size: 11px;"
                    "padding: 6px 4px;"
                    "text-align: center;"
                    "opacity: 0.5;"
                )
            else:
                self.setStyleSheet(
                    "background-color: #161B22;"
                    "border: 1px solid #30363D;"
                    "border-radius: 6px;"
                    "color: #E6EDF3;"
                    "font-size: 11px;"
                    "padding: 6px 4px;"
                    "text-align: center;"
                )

    def is_selected(self) -> bool:
        return self._is_selected

    def brand_key(self) -> str:
        return self._brand_key

    def brand_info(self) -> BrandInfo:
        return self._brand_info


class BrandSelector(QWidget):
    """
    Grid of brand selection buttons.

    Emits `brand_selected(brand_key: str)` when a brand is clicked.
    """

    brand_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_key: str | None = None
        self._buttons: dict[str, BrandButton] = {}
        self._setup_ui()
        self._populate_brands()

    def _setup_ui(self):
        # Wrap in a scroll area for many brands
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setMinimumHeight(180)
        scroll.setMaximumHeight(220)
        scroll.setStyleSheet(
            "background-color: transparent;"
            "border: none;"
        )

        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(8)
        grid.setContentsMargins(0, 0, 0, 0)

        # 4 columns
        self._grid = grid

        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _populate_brands(self):
        """Populate the grid with brand buttons."""
        brands_working = []
        brands_coming = []

        for key, info in BRAND_REGISTRY.items():
            if info.status == "working":
                brands_working.append((key, info))
            else:
                brands_coming.append((key, info))

        sorted_brands = brands_working + brands_coming
        self._buttons.clear()

        row = 0
        col = 0
        for key, info in sorted_brands:
            btn = BrandButton(key, info)
            btn.clicked.connect(lambda checked, k=key: self._on_button_clicked(k))
            self._grid.addWidget(btn, row, col)
            self._buttons[key] = btn
            col += 1
            if col >= 4:
                col = 0
                row += 1

    def _on_button_clicked(self, key: str) -> None:
        """Handle brand button click."""
        info = BRAND_REGISTRY.get(key)
        if info and info.status == "coming_soon":
            # Still select it, but main window will show "coming soon" message
            pass
        self._select_brand(key)
        self.brand_selected.emit(key)

    def _select_brand(self, key: str) -> None:
        """Update selection state of all buttons."""
        # Deselect previous
        if self._selected_key and self._selected_key in self._buttons:
            self._buttons[self._selected_key].set_selected(False)

        self._selected_key = key

        # Select new
        if key in self._buttons:
            self._buttons[key].set_selected(True)

    def select_brand(self, key: str) -> None:
        """Programmatically select a brand."""
        if key in self._buttons:
            self._select_brand(key)

    def selected_brand(self) -> str | None:
        """Return the currently selected brand key."""
        return self._selected_key
