"""Main window: password display, length slider, character set checkboxes
and a copy-to-clipboard button.

The window only reads the controls, builds an Options object and asks
password_core for a password. It does not generate anything itself.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from password_core import Options, entropy_bits, generate_password, pool_size, strength_label

from .theme import STRENGTH_COLORS, mono_font

SLIDER_MIN = 4
SLIDER_MAX = 64
DEFAULT_LENGTH = 16
COPIED_FEEDBACK_MS = 1500


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Password Generator")
        self.setMinimumWidth(520)

        self._build_ui()
        self._connect_signals()
        self.regenerate()

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        # --- Password card: [password text] [strength] [regenerate] ------
        self.password_field = QLineEdit(objectName="password")
        self.password_field.setReadOnly(True)
        self.password_field.setFont(mono_font())

        self.strength_label = QLabel()
        self.regenerate_button = QPushButton("⟳")
        self.regenerate_button.setToolTip("Generate a new password")
        self.regenerate_button.setFixedWidth(40)
        self.regenerate_button.setStyleSheet("font-size: 18px; padding: 2px;")

        card = QFrame(objectName="card")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 10, 10, 10)
        card_layout.addWidget(self.password_field, stretch=1)
        card_layout.addWidget(self.strength_label)
        card_layout.addWidget(self.regenerate_button)

        self.copy_button = QPushButton("Copy", objectName="accent")
        self.copy_button.setMinimumHeight(40)

        # --- Length row: "Length" [slider] 16 -----------------------------
        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setRange(SLIDER_MIN, SLIDER_MAX)
        self.length_slider.setValue(DEFAULT_LENGTH)
        self.length_value = QLabel(str(DEFAULT_LENGTH))
        self.length_value.setFixedWidth(28)
        self.length_value.setAlignment(Qt.AlignmentFlag.AlignRight)

        length_row = QHBoxLayout()
        length_row.addWidget(QLabel("Length", objectName="secondary"))
        length_row.addWidget(self.length_slider, stretch=1)
        length_row.addWidget(self.length_value)

        # --- Character set checkboxes ------------------------------------
        self.upper_box = QCheckBox("ABC")
        self.lower_box = QCheckBox("abc")
        self.digits_box = QCheckBox("123")
        self.symbols_box = QCheckBox("#$&&")  # "&&" shows a literal "&" (a single "&" marks a keyboard shortcut in Qt)
        self.checkboxes = [self.upper_box, self.lower_box, self.digits_box, self.symbols_box]
        for box in (self.upper_box, self.lower_box, self.digits_box):
            box.setChecked(True)

        chars_row = QHBoxLayout()
        chars_row.addWidget(QLabel("Characters", objectName="secondary"))
        chars_row.addStretch()
        for box in self.checkboxes:
            chars_row.addWidget(box)

        # --- Put everything together -------------------------------------
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(18)
        root.addWidget(card)
        root.addWidget(self.copy_button)
        root.addSpacing(6)
        root.addLayout(length_row)
        root.addLayout(chars_row)

    def _connect_signals(self) -> None:
        # Signals and slots: "when X happens, call this method".
        self.regenerate_button.clicked.connect(self.regenerate)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.length_slider.valueChanged.connect(self._on_length_changed)
        for box in self.checkboxes:
            box.toggled.connect(self._on_checkbox_toggled)

    # ------------------------------------------------------------- Actions
    def current_options(self) -> Options:
        return Options(
            length=self.length_slider.value(),
            upper=self.upper_box.isChecked(),
            lower=self.lower_box.isChecked(),
            digits=self.digits_box.isChecked(),
            symbols=self.symbols_box.isChecked(),
        )

    def regenerate(self) -> None:
        opts = self.current_options()
        self.password_field.setText(generate_password(opts))
        self.password_field.setCursorPosition(0)  # show the start of long passwords

        bits = entropy_bits(opts.length, pool_size(opts))
        label = strength_label(bits)
        self.strength_label.setText(label)
        self.strength_label.setToolTip(f"{bits:.0f} bits of entropy")
        self.strength_label.setStyleSheet(
            f"color: {STRENGTH_COLORS[label]}; font-weight: 600;"
        )

    def copy_to_clipboard(self) -> None:
        QGuiApplication.clipboard().setText(self.password_field.text())
        self.copy_button.setText("Copied ✓")
        QTimer.singleShot(COPIED_FEEDBACK_MS, lambda: self.copy_button.setText("Copy"))

    def _on_length_changed(self, value: int) -> None:
        self.length_value.setText(str(value))
        self.regenerate()

    def _on_checkbox_toggled(self, checked: bool) -> None:
        # At least one character set must stay selected: if the user just
        # unchecked the last one, check it again.
        if not any(box.isChecked() for box in self.checkboxes):
            box = self.sender()
            box.blockSignals(True)   # avoid triggering this method again
            box.setChecked(True)
            box.blockSignals(False)
            return
        self.regenerate()
