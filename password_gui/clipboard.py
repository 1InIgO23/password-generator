"""Copy text to the clipboard and clear it automatically after a delay.

Passwords left in the clipboard can be pasted by accident later, or read
by any program running on the computer. Clearing them after a short time
reduces that risk.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import QByteArray, QMimeData, QObject, QTimer, Signal
from PySide6.QtGui import QGuiApplication

# Windows clipboard format that asks Windows not to store the copied text in
# the clipboard history (Win+V) or sync it to other devices. Password managers
# such as KeePassXC use the same format. Other systems simply ignore it.
_WINDOWS_EXCLUDE_FROM_HISTORY = (
    'application/x-qt-windows-mime;value="ExcludeClipboardContentFromMonitorProcessing"'
)


class ClipboardGuard(QObject):
    """Copies text and removes it from the clipboard after `timeout_s` seconds.

    Signals:
        tick(int): emitted every second with the seconds left before clearing.
        cleared(): emitted when the countdown ends (whether or not the
            clipboard still held our text).
    """

    tick = Signal(int)
    cleared = Signal()

    def __init__(self, timeout_s: int = 20, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.timeout_s = timeout_s
        self._text: str | None = None
        self._remaining = 0

        self._timer = QTimer(self)
        self._timer.setInterval(1000)   # fire once per second
        self._timer.timeout.connect(self._on_tick)

    @property
    def remaining(self) -> int:
        """Seconds left before clearing (0 when nothing is pending)."""
        return self._remaining

    def copy(self, text: str) -> None:
        """Put `text` on the clipboard and (re)start the countdown."""
        mime = QMimeData()
        mime.setText(text)
        if sys.platform == "win32":
            mime.setData(_WINDOWS_EXCLUDE_FROM_HISTORY, QByteArray(b"\x00\x00\x00\x00"))
        QGuiApplication.clipboard().setMimeData(mime)

        self._text = text
        self._remaining = self.timeout_s
        self._timer.start()
        self.tick.emit(self._remaining)

    def clear_now(self) -> None:
        """Clear the clipboard immediately if it still holds our text."""
        self._timer.stop()
        self._remaining = 0
        clipboard = QGuiApplication.clipboard()
        # Only clear if the clipboard still contains what we copied: if the
        # user copied something else in the meantime, we must not delete it.
        if self._text is not None and clipboard.text() == self._text:
            clipboard.clear()
        self._text = None

    def _on_tick(self) -> None:
        self._remaining -= 1
        if self._remaining > 0:
            self.tick.emit(self._remaining)
        else:
            self.clear_now()
            self.cleared.emit()
