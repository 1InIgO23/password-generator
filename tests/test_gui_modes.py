"""Tests for the Password / Passphrase modes of the main window.

They run without showing any window ("offscreen" platform) and are skipped
automatically if PySide6 is not installed.
"""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtWidgets import QApplication
except ImportError:  # PySide6 not installed: skip this whole file
    raise unittest.SkipTest("PySide6 is not installed")

from password_core import load_wordlist
from password_gui.main_window import PASSPHRASE_MODE, PASSWORD_MODE, MainWindow
from password_gui.panels import PASSPHRASE_DEFAULT_WORDS, PASSWORD_DEFAULT_LENGTH
from password_gui.theme import MONO_FONTS, UI_FONTS

app = QApplication.instance() or QApplication([])


class ModeTests(unittest.TestCase):
    def setUp(self):
        self.window = MainWindow()

    def tearDown(self):
        self.window.close()

    def result(self) -> str:
        return self.window.password_field.text()

    def test_starts_in_password_mode(self):
        self.assertEqual(self.window.mode_selector.currentIndex(), PASSWORD_MODE)
        self.assertEqual(len(self.result()), PASSWORD_DEFAULT_LENGTH)
        self.assertNotIn("-", self.result())   # symbols are off by default

    def test_switching_to_passphrase(self):
        self.window.mode_selector.setCurrentIndex(PASSPHRASE_MODE)
        words = self.result().split("-")
        self.assertEqual(len(words), PASSPHRASE_DEFAULT_WORDS)
        self.assertTrue(all(w[0].isupper() for w in words))          # Capitalize on
        self.assertEqual(sum(c.isdigit() for c in self.result()), 1)  # Number on

    def test_passphrase_words_come_from_wordlist(self):
        self.window.mode_selector.setCurrentIndex(PASSPHRASE_MODE)
        self.window.passphrase_panel.capitalize_box.setChecked(False)
        self.window.passphrase_panel.number_box.setChecked(False)
        wordlist = set(load_wordlist())
        self.assertTrue(set(self.result().split("-")) <= wordlist)

    def test_word_slider(self):
        self.window.mode_selector.setCurrentIndex(PASSPHRASE_MODE)
        self.window.passphrase_panel.slider.setValue(9)
        self.assertEqual(len(self.result().split("-")), 9)

    def test_each_mode_remembers_its_settings(self):
        self.window.password_panel.slider.setValue(30)
        self.window.mode_selector.setCurrentIndex(PASSPHRASE_MODE)
        self.window.passphrase_panel.slider.setValue(4)
        self.window.mode_selector.setCurrentIndex(PASSWORD_MODE)
        self.assertEqual(len(self.result()), 30)
        self.window.mode_selector.setCurrentIndex(PASSPHRASE_MODE)
        self.assertEqual(len(self.result().split("-")), 4)

    def test_font_changes_with_mode(self):
        self.assertEqual(self.window.password_field.font().families(), MONO_FONTS)
        self.window.mode_selector.setCurrentIndex(PASSPHRASE_MODE)
        self.assertEqual(self.window.password_field.font().families(), UI_FONTS)

    def test_cannot_uncheck_every_character_set(self):
        panel = self.window.password_panel
        for box in panel.checkboxes:
            box.setChecked(False)
        self.assertEqual(sum(box.isChecked() for box in panel.checkboxes), 1)

    def test_strength_label_updates(self):
        self.window.password_panel.slider.setValue(4)
        self.assertEqual(self.window.strength_label.text(), "Weak")
        self.window.mode_selector.setCurrentIndex(PASSPHRASE_MODE)
        self.assertEqual(self.window.strength_label.text(), "Very strong")

    def test_copy_works_in_passphrase_mode(self):
        self.window.mode_selector.setCurrentIndex(PASSPHRASE_MODE)
        self.window.copy_button.click()
        self.assertEqual(QApplication.clipboard().text(), self.result())


if __name__ == "__main__":
    unittest.main()
