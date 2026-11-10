"""Windows 11 dark mode look: colors, fonts and the Qt style sheet."""

from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

# Windows 11 dark mode palette (approximate values from the Fluent design system).
BACKGROUND = "#202020"     # window background
SURFACE = "#2b2b2b"        # cards and input fields
SURFACE_HOVER = "#323232"
SEGMENT_SELECTED = "#3d3d3d"  # selected segment in the mode selector
BORDER = "#3a3a3a"
TEXT = "#ffffff"
TEXT_SECONDARY = "#c5c5c5"
ACCENT = "#60cdff"         # default Windows 11 accent in dark mode
ACCENT_HOVER = "#7ad5ff"
ACCENT_TEXT = "#000000"    # text drawn on top of the accent color

# Colors for each strength label returned by password_core.strength_label().
STRENGTH_COLORS = {
    "Weak": "#ff99a4",
    "Fair": "#fce100",
    "Strong": "#6ccb5f",
    "Very strong": "#6ccb5f",
}

# Qt tries each font in order and uses the first one installed on the system.
UI_FONTS = ["Segoe UI Variable", "Segoe UI", "SF Pro Text", "Ubuntu", "Cantarell", "sans-serif"]
MONO_FONTS = ["Cascadia Mono", "Consolas", "SF Mono", "Menlo", "DejaVu Sans Mono", "monospace"]

STYLE_SHEET = f"""
QWidget {{
    background-color: {BACKGROUND};
    color: {TEXT};
    font-size: 14px;
}}

QLabel#secondary {{
    color: {TEXT_SECONDARY};
}}

QFrame#card {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
QFrame#card QWidget {{
    background-color: transparent;
}}

QLineEdit#password {{
    background-color: transparent;
    border: none;
    font-size: 20px;
    selection-background-color: {ACCENT};
    selection-color: {ACCENT_TEXT};
}}

QPushButton {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 14px;
}}
QPushButton:hover {{
    background-color: {SURFACE_HOVER};
}}
QPushButton#accent {{
    background-color: {ACCENT};
    color: {ACCENT_TEXT};
    border: none;
    font-weight: 600;
}}
QPushButton#accent:hover {{
    background-color: {ACCENT_HOVER};
}}

QFrame#segmented {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 7px;
}}
QPushButton#segment {{
    background-color: transparent;
    color: {TEXT_SECONDARY};
    border: none;
    border-radius: 5px;
    padding: 5px 16px;
}}
QPushButton#segment:hover {{
    color: {TEXT};
}}
QPushButton#segment:checked {{
    background-color: {SEGMENT_SELECTED};
    color: {TEXT};
    font-weight: 600;
}}

QSlider::groove:horizontal {{
    height: 4px;
    background: {BORDER};
    border-radius: 2px;
}}
QSlider::sub-page:horizontal {{
    background: {ACCENT};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {ACCENT};
    border: 4px solid {SURFACE};
    width: 12px;
    height: 12px;
    margin: -8px 0;
    border-radius: 10px;
}}

QCheckBox {{
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid {TEXT_SECONDARY};
}}
QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border: 1px solid {ACCENT};
}}
"""


def ui_font(point_size: int = 10) -> QFont:
    font = QFont()
    font.setFamilies(UI_FONTS)
    font.setPointSize(point_size)
    return font


def mono_font(point_size: int = 14) -> QFont:
    font = QFont()
    font.setFamilies(MONO_FONTS)
    font.setPointSize(point_size)
    font.setStyleHint(QFont.StyleHint.Monospace)
    return font


def apply_theme(app: QApplication) -> None:
    """Apply the dark theme to the whole application."""
    app.setStyle("Fusion")   # same base look on Windows, Linux and macOS
    app.setFont(ui_font())
    app.setStyleSheet(STYLE_SHEET)
