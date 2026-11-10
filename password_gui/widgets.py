"""Reusable custom widgets."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QButtonGroup, QFrame, QHBoxLayout, QPushButton


class SegmentedControl(QFrame):
    """A row of mutually exclusive buttons, like the selector bars in
    Windows 11 Settings. Exactly one segment is selected at any time.

    Signals:
        currentChanged(int): index of the newly selected segment.
    """

    currentChanged = Signal(int)

    def __init__(self, labels: list[str], parent=None) -> None:
        super().__init__(parent, objectName="segmented")

        # QButtonGroup with exclusive=True: checking one button unchecks the others.
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        for index, label in enumerate(labels):
            button = QPushButton(label, objectName="segment")
            button.setCheckable(True)
            self._group.addButton(button, index)   # the id is the segment index
            layout.addWidget(button)

        self._group.button(0).setChecked(True)
        self._group.idClicked.connect(self.currentChanged)

    def currentIndex(self) -> int:
        return self._group.checkedId()

    def setCurrentIndex(self, index: int) -> None:
        """Select a segment from code (emits currentChanged if it changes)."""
        if index != self.currentIndex():
            self._group.button(index).setChecked(True)
            self.currentChanged.emit(index)
