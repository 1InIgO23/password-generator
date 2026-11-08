import math
import unittest

from password_core import (
    MAX_LENGTH,
    MIN_LENGTH,
    Options,
    entropy_bits,
    generate_password,
    pool_size,
    strength_label,
)
from password_core.generator import AMBIGUOUS, DIGITS, LOWER, SYMBOLS, UPPER


class GenerateTests(unittest.TestCase):
    def test_length_matches_option(self):
        for length in (MIN_LENGTH, 12, 16, 64, MAX_LENGTH):
            with self.subTest(length=length):
                self.assertEqual(len(generate_password(Options(length=length))), length)

    def test_every_selected_class_is_present(self):
        opts = Options(length=8, upper=True, lower=True, digits=True, symbols=True)
        for _ in range(300):
            pw = generate_password(opts)
            self.assertTrue(any(c in UPPER for c in pw), pw)
            self.assertTrue(any(c in LOWER for c in pw), pw)
            self.assertTrue(any(c in DIGITS for c in pw), pw)
            self.assertTrue(any(c in SYMBOLS for c in pw), pw)

    def test_disabled_classes_are_absent(self):
        opts = Options(length=32, upper=False, lower=True, digits=False, symbols=False)
        for _ in range(100):
            pw = generate_password(opts)
            self.assertTrue(all(c in LOWER for c in pw), pw)

    def test_symbols_only_when_enabled(self):
        opts = Options(length=32, symbols=True)
        self.assertTrue(
            any(any(c in SYMBOLS for c in generate_password(opts)) for _ in range(20))
        )

    def test_exclude_ambiguous(self):
        opts = Options(length=64, exclude_ambiguous=True, symbols=True)
        for _ in range(100):
            pw = generate_password(opts)
            self.assertFalse(set(pw) & AMBIGUOUS, pw)

    def test_passwords_are_not_repeated(self):
        opts = Options(length=16)
        generated = {generate_password(opts) for _ in range(1000)}
        self.assertEqual(len(generated), 1000)

    def test_no_classes_raises(self):
        with self.assertRaises(ValueError):
            generate_password(Options(upper=False, lower=False, digits=False))

    def test_length_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            generate_password(Options(length=MIN_LENGTH - 1))
        with self.assertRaises(ValueError):
            generate_password(Options(length=MAX_LENGTH + 1))


class PoolAndEntropyTests(unittest.TestCase):
    def test_pool_size_default(self):
        # uppercase + lowercase + digits
        self.assertEqual(pool_size(Options()), 62)

    def test_pool_size_with_symbols(self):
        self.assertEqual(pool_size(Options(symbols=True)), 62 + len(SYMBOLS))

    def test_pool_size_excluding_ambiguous(self):
        self.assertEqual(pool_size(Options(exclude_ambiguous=True)), 62 - len(AMBIGUOUS))

    def test_entropy_of_16_chars_alnum(self):
        self.assertAlmostEqual(entropy_bits(16, 62), 16 * math.log2(62))

    def test_entropy_degenerate_inputs(self):
        self.assertEqual(entropy_bits(0, 62), 0.0)
        self.assertEqual(entropy_bits(16, 1), 0.0)

    def test_strength_labels(self):
        self.assertEqual(strength_label(10), "Débil")
        self.assertEqual(strength_label(50), "Razonable")
        self.assertEqual(strength_label(70), "Fuerte")
        self.assertEqual(strength_label(100), "Muy segura")


if __name__ == "__main__":
    unittest.main()
