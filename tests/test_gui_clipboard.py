"""Tests for the clipboard auto-clear feature.

They run without showing any window ("offscreen" platform) and are skipped
automatically if PySide6 is not installed.
"""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
except ImportError:  # PySide6 not installed: skip this whole file
    raise unittest.SkipTest("PySide6 is not installed")

from password_gui.clipboard import ClipboardGuard
from password_gui.main_window import MainWindow

app = QApplication.instance() or QApplication([])


def clipboard_text() -> str:
    return QApplication.clipboard().text()


class ClipboardGuardTests(unittest.TestCase):
    def setUp(self):
        QApplication.clipboard().clear()
        self.guard = ClipboardGuard(timeout_s=1)

    def test_copy_puts_text_on_clipboard(self):
        self.guard.copy("secret")
        self.assertEqual(clipboard_text(), "secret")
        self.assertEqual(self.guard.remaining, 1)

    def test_clipboard_is_cleared_after_timeout(self):
        self.guard.copy("secret")
        QTest.qWait(1300)   # let the event loop run for 1.3 s
        self.assertEqual(clipboard_text(), "")
        self.assertEqual(self.guard.remaining, 0)

    def test_does_not_clear_text_copied_by_someone_else(self):
        self.guard.copy("secret")
        QApplication.clipboard().setText("something the user copied later")
        QTest.qWait(1300)
        self.assertEqual(clipboard_text(), "something the user copied later")

    def test_copying_again_restarts_the_countdown(self):
        guard = ClipboardGuard(timeout_s=2)
        guard.copy("first")
        QTest.qWait(1100)
        guard.copy("second")
        self.assertEqual(guard.remaining, 2)
        QTest.qWait(1100)   # 2.2 s after the first copy, 1.1 s after the second
        self.assertEqual(clipboard_text(), "second")

    def test_signals(self):
        ticks, cleared = [], []
        guard = ClipboardGuard(timeout_s=2)
        guard.tick.connect(ticks.append)
        guard.cleared.connect(lambda: cleared.append(True))
        guard.copy("secret")
        QTest.qWait(2300)
        self.assertEqual(ticks, [2, 1])
        self.assertEqual(cleared, [True])


class MainWindowClipboardTests(unittest.TestCase):
    def setUp(self):
        QApplication.clipboard().clear()
        self.window = MainWindow(clipboard_timeout_s=1)

    def tearDown(self):
        self.window.close()

    def test_copy_button_copies_password_and_shows_countdown(self):
        self.window.copy_button.click()
        self.assertEqual(clipboard_text(), self.window.password_field.text())
        self.assertIn("clears in", self.window.clipboard_status.text())

    def test_status_after_clearing(self):
        self.window.copy_button.click()
        QTest.qWait(1300)
        self.assertEqual(clipboard_text(), "")
        self.assertEqual(self.window.clipboard_status.text(), "Clipboard cleared")

    def test_closing_the_window_clears_the_clipboard(self):
        window = MainWindow(clipboard_timeout_s=60)
        window.copy_button.click()
        window.close()
        self.assertEqual(clipboard_text(), "")


if __name__ == "__main__":
    unittest.main()
