"""Options panels: one for passwords and one for passphrases.

Both panels share the same small interface, so the main window can use
whichever is visible without knowing which one it is:

    changed           signal emitted when any option changes
    generate()        returns (text, entropy_bits)
    monospace         True if the result should be shown in a monospace font
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QGridLayout, QHBoxLayout, QLabel, QSlider, QWidget

from password_core import (
    Options,
    PassphraseOptions,
    entropy_bits,
    generate_passphrase,
    generate_password,
    passphrase_entropy_bits,
    pool_size,
)
from password_core.passphrase import MIN_WORDS

PASSWORD_MIN_LENGTH = 4
PASSWORD_MAX_LENGTH = 64
PASSWORD_DEFAULT_LENGTH = 16

PASSPHRASE_MAX_WORDS = 12
PASSPHRASE_DEFAULT_WORDS = 6
PASSPHRASE_SEPARATOR = "-"   # hyphen: accepted by almost every website


class _OptionsPanel(QWidget):
    """Common layout: a grid with a "slider" row and a "checkboxes" row.

    Both panels use the same grid so they have exactly the same height and
    their labels line up; switching modes doesn't make the window jump.
    """

    changed = Signal()
    monospace = True

    def __init__(self, slider_label: str, boxes_label: str,
                 minimum: int, maximum: int, default: int) -> None:
        super().__init__()

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(minimum, maximum)
        self.slider.setValue(default)
        self.slider_value = QLabel(str(default))
        self.slider_value.setFixedWidth(28)
        self.slider_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.slider.valueChanged.connect(self._on_slider_changed)

        self.boxes_row = QHBoxLayout()
        self.boxes_row.setSpacing(18)
        self.boxes_row.addStretch()

        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(18)
        grid.addWidget(QLabel(slider_label, objectName="secondary"), 0, 0)
        grid.addWidget(self.slider, 0, 1)
        grid.addWidget(self.slider_value, 0, 2)
        grid.addWidget(QLabel(boxes_label, objectName="secondary"), 1, 0)
        grid.addLayout(self.boxes_row, 1, 1, 1, 2)   # spans two columns
        grid.setColumnMinimumWidth(0, 80)
        grid.setColumnStretch(1, 1)

    def _add_checkbox(self, text: str, checked: bool) -> QCheckBox:
        box = QCheckBox(text)
        box.setChecked(checked)
        box.toggled.connect(self._on_checkbox_toggled)
        self.boxes_row.addWidget(box)
        return box

    def _on_slider_changed(self, value: int) -> None:
        self.slider_value.setText(str(value))
        self.changed.emit()

    def _on_checkbox_toggled(self, checked: bool) -> None:
        self.changed.emit()

    def generate(self) -> tuple[str, float]:
        raise NotImplementedError   # each subclass provides its own


class PasswordPanel(_OptionsPanel):
    monospace = True

    def __init__(self) -> None:
        super().__init__("Length", "Characters",
                         PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH, PASSWORD_DEFAULT_LENGTH)
        self.upper_box = self._add_checkbox("ABC", True)
        self.lower_box = self._add_checkbox("abc", True)
        self.digits_box = self._add_checkbox("123", True)
        # "&&" shows a literal "&" (a single "&" marks a keyboard shortcut in Qt)
        self.symbols_box = self._add_checkbox("#$&&", False)
        self.checkboxes = [self.upper_box, self.lower_box, self.digits_box, self.symbols_box]

    def options(self) -> Options:
        return Options(
            length=self.slider.value(),
            upper=self.upper_box.isChecked(),
            lower=self.lower_box.isChecked(),
            digits=self.digits_box.isChecked(),
            symbols=self.symbols_box.isChecked(),
        )

    def generate(self) -> tuple[str, float]:
        opts = self.options()
        return generate_password(opts), entropy_bits(opts.length, pool_size(opts))

    def _on_checkbox_toggled(self, checked: bool) -> None:
        # At least one character set must stay selected: if the user just
        # unchecked the last one, check it again.
        if not any(box.isChecked() for box in self.checkboxes):
            box = self.sender()
            box.blockSignals(True)   # avoid triggering this method again
            box.setChecked(True)
            box.blockSignals(False)
            return
        self.changed.emit()


class PassphrasePanel(_OptionsPanel):
    monospace = False   # words read better in the normal font, and fit in the field

    def __init__(self) -> None:
        super().__init__("Words", "Options",
                         MIN_WORDS, PASSPHRASE_MAX_WORDS, PASSPHRASE_DEFAULT_WORDS)
        self.capitalize_box = self._add_checkbox("Capitalize", True)
        self.number_box = self._add_checkbox("Number", True)

    def options(self) -> PassphraseOptions:
        return PassphraseOptions(
            words=self.slider.value(),
            separator=PASSPHRASE_SEPARATOR,
            capitalize=self.capitalize_box.isChecked(),
            add_number=self.number_box.isChecked(),
        )

    def generate(self) -> tuple[str, float]:
        opts = self.options()
        return generate_passphrase(opts), passphrase_entropy_bits(opts)
