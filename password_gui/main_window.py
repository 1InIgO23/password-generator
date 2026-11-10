"""Main window.

Layout, top to bottom:
    [ Password | Passphrase ]      mode selector
    [ result      strength  ⟳ ]    shared by both modes
    [          Copy           ]    shared by both modes
    clipboard status line
    options panel                  changes with the selected mode

The window only asks the visible panel for a result. It does not generate
anything itself, and it doesn't need to know which mode is active.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from password_core import strength_label

from .clipboard import ClipboardGuard
from .panels import PassphrasePanel, PasswordPanel
from .theme import STRENGTH_COLORS, mono_font, ui_font
from .widgets import SegmentedControl

COPIED_FEEDBACK_MS = 1500
CLIPBOARD_CLEAR_SECONDS = 20
CLEARED_MESSAGE_MS = 2500
PASSPHRASE_FONT_PT = 11   # at 640 px, about 95% of 6-word phrases fit without scrolling

PASSWORD_MODE = 0
PASSPHRASE_MODE = 1


class MainWindow(QWidget):
    def __init__(self, clipboard_timeout_s: int = CLIPBOARD_CLEAR_SECONDS) -> None:
        super().__init__()
        self.setWindowTitle("Password Generator")
        self.setMinimumWidth(640)   # wide enough for a 6-word passphrase

        self.clipboard_guard = ClipboardGuard(clipboard_timeout_s, parent=self)

        self._build_ui()
        self._connect_signals()
        self.regenerate()

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        # --- Mode selector -----------------------------------------------
        self.mode_selector = SegmentedControl(["Password", "Passphrase"])

        # --- Result card: [text] [strength] [regenerate] ------------------
        self.password_field = QLineEdit(objectName="password")
        self.password_field.setReadOnly(True)

        self.strength_label = QLabel()
        self.regenerate_button = QPushButton("⟳")
        self.regenerate_button.setToolTip("Generate a new one")
        self.regenerate_button.setFixedWidth(40)
        self.regenerate_button.setStyleSheet("font-size: 18px; padding: 2px;")

        card = QFrame(objectName="card")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 10, 10, 10)
        card_layout.addWidget(self.password_field, stretch=1)
        card_layout.addWidget(self.strength_label)
        card_layout.addWidget(self.regenerate_button)

        # --- Copy button and clipboard status ----------------------------
        self.copy_button = QPushButton("Copy", objectName="accent")
        self.copy_button.setMinimumHeight(40)

        # It always keeps its height so the layout doesn't jump when it changes.
        self.clipboard_status = QLabel("", objectName="secondary")
        self.clipboard_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clipboard_status.setStyleSheet("font-size: 12px;")
        self.clipboard_status.setFixedHeight(self.clipboard_status.sizeHint().height() + 4)

        # --- Options: one panel per mode, only one visible at a time -----
        self.password_panel = PasswordPanel()
        self.passphrase_panel = PassphrasePanel()
        self.options_stack = QStackedWidget()
        self.options_stack.addWidget(self.password_panel)     # index 0 = PASSWORD_MODE
        self.options_stack.addWidget(self.passphrase_panel)   # index 1 = PASSPHRASE_MODE

        # --- Put everything together -------------------------------------
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 24)
        root.setSpacing(18)
        root.addWidget(self.mode_selector, alignment=Qt.AlignmentFlag.AlignLeft)
        root.addWidget(card)
        root.addWidget(self.copy_button)
        root.addWidget(self.clipboard_status)
        root.addWidget(self.options_stack)

    def _connect_signals(self) -> None:
        self.mode_selector.currentChanged.connect(self._on_mode_changed)
        self.regenerate_button.clicked.connect(self.regenerate)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.password_panel.changed.connect(self.regenerate)
        self.passphrase_panel.changed.connect(self.regenerate)
        self.clipboard_guard.tick.connect(self._on_clipboard_tick)
        self.clipboard_guard.cleared.connect(self._on_clipboard_cleared)

    # ------------------------------------------------------------- Actions
    def current_panel(self):
        return self.options_stack.currentWidget()

    def regenerate(self) -> None:
        panel = self.current_panel()
        text, bits = panel.generate()

        self.password_field.setFont(mono_font() if panel.monospace else ui_font(PASSPHRASE_FONT_PT))
        self.password_field.setText(text)
        self.password_field.setCursorPosition(0)  # show the start of long results

        label = strength_label(bits)
        self.strength_label.setText(label)
        self.strength_label.setToolTip(f"{bits:.0f} bits of entropy")
        self.strength_label.setStyleSheet(
            f"color: {STRENGTH_COLORS[label]}; font-weight: 600;"
        )

    def copy_to_clipboard(self) -> None:
        self.clipboard_guard.copy(self.password_field.text())
        self.copy_button.setText("Copied ✓")
        QTimer.singleShot(COPIED_FEEDBACK_MS, lambda: self.copy_button.setText("Copy"))

    def _on_mode_changed(self, index: int) -> None:
        self.options_stack.setCurrentIndex(index)
        self.regenerate()

    def _on_clipboard_tick(self, seconds_left: int) -> None:
        self.clipboard_status.setText(f"Clipboard clears in {seconds_left} s")

    def _on_clipboard_cleared(self) -> None:
        self.clipboard_status.setText("Clipboard cleared")
        QTimer.singleShot(CLEARED_MESSAGE_MS, self._hide_cleared_message)

    def _hide_cleared_message(self) -> None:
        # Don't erase a new countdown if the user copied again in the meantime.
        if self.clipboard_guard.remaining == 0:
            self.clipboard_status.setText("")

    def closeEvent(self, event: QCloseEvent) -> None:
        """Called by Qt when the window is closing: don't leave the password behind."""
        self.clipboard_guard.clear_now()
        super().closeEvent(event)
