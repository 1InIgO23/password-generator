import io
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout

from password_core.cli import main
from password_core.generator import SYMBOLS


def run(*argv: str) -> tuple[int, str, str]:
    """Call the CLI in-process and capture (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = main(list(argv))
        except SystemExit as e:  # argparse exits on errors and on --help
            code = e.code
    return code, out.getvalue(), err.getvalue()


class PasswordCommandTests(unittest.TestCase):
    def test_default(self):
        code, out, _ = run("password")
        self.assertEqual(code, 0)
        self.assertEqual(len(out.strip()), 16)

    def test_length_and_symbols(self):
        code, out, _ = run("password", "--length", "30", "--symbols")
        pw = out.strip()
        self.assertEqual(code, 0)
        self.assertEqual(len(pw), 30)
        self.assertTrue(any(c in SYMBOLS for c in pw))

    def test_digits_only(self):
        _, out, _ = run("password", "--no-upper", "--no-lower")
        self.assertTrue(out.strip().isdigit())

    def test_count(self):
        _, out, _ = run("password", "--count", "5")
        self.assertEqual(len(out.splitlines()), 5)

    def test_entropy_goes_to_stderr(self):
        _, out, err = run("password", "--entropy")
        self.assertEqual(len(out.splitlines()), 1)   # stdout: only the password
        self.assertIn("bits", err)


class PassphraseCommandTests(unittest.TestCase):
    def test_words_and_separator(self):
        code, out, _ = run("passphrase", "--words", "4", "--separator", ".")
        self.assertEqual(code, 0)
        self.assertEqual(len(out.strip().split(".")), 4)

    def test_capitalize_and_number(self):
        _, out, _ = run("passphrase", "--capitalize", "--number")
        phrase = out.strip()
        self.assertTrue(all(w[0].isupper() for w in phrase.split("-")))
        self.assertEqual(sum(c.isdigit() for c in phrase), 1)


class ErrorTests(unittest.TestCase):
    def test_no_command_fails(self):
        code, _, err = run()
        self.assertEqual(code, 2)
        self.assertIn("usage", err)

    def test_invalid_length_shows_clean_message(self):
        code, out, err = run("password", "--length", "2")
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("Length must be between", err)
        self.assertNotIn("Traceback", err)

    def test_no_character_classes(self):
        code, _, err = run("password", "--no-upper", "--no-lower", "--no-digits")
        self.assertEqual(code, 2)
        self.assertIn("at least one character set", err)

    def test_invalid_count(self):
        for bad in ("0", "101", "abc"):
            with self.subTest(count=bad):
                code, _, _ = run("password", "--count", bad)
                self.assertEqual(code, 2)


class ModuleEntryPointTests(unittest.TestCase):
    def test_python_dash_m(self):
        """`python -m password_core` works as a real process."""
        result = subprocess.run(
            [sys.executable, "-m", "password_core", "passphrase", "--words", "3"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(result.stdout.strip().split("-")), 3)


if __name__ == "__main__":
    unittest.main()
