"""Makes `python -m password_gui` open the window."""

import sys

from PySide6.QtWidgets import QApplication

from .main_window import MainWindow
from .theme import apply_theme


def main() -> int:
    app = QApplication(sys.argv)
    apply_theme(app)
    window = MainWindow()
    window.show()
    return app.exec()  # runs the event loop until the window is closed


if __name__ == "__main__":
    sys.exit(main())
