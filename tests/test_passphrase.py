import math
import unittest

from password_core import (
    PassphraseOptions,
    generate_passphrase,
    load_wordlist,
    passphrase_entropy_bits,
)
from password_core.passphrase import MAX_WORDS, MIN_WORDS


class WordlistTests(unittest.TestCase):
    def test_wordlist_is_large_and_clean(self):
        words = load_wordlist()
        self.assertGreater(len(words), 7000)
        self.assertEqual(len(words), len(set(words)))       # sin duplicados
        self.assertTrue(all(w.isalpha() and w.islower() for w in words))


class PassphraseTests(unittest.TestCase):
    def test_word_count_and_separator(self):
        for n in (MIN_WORDS, 6, MAX_WORDS):
            with self.subTest(words=n):
                phrase = generate_passphrase(PassphraseOptions(words=n, separator="."))
                self.assertEqual(len(phrase.split(".")), n)

    def test_words_come_from_wordlist(self):
        words = set(load_wordlist())
        for _ in range(100):
            for w in generate_passphrase().split("-"):
                self.assertIn(w, words)

    def test_capitalize(self):
        phrase = generate_passphrase(PassphraseOptions(capitalize=True))
        self.assertTrue(all(w[0].isupper() for w in phrase.split("-")))

    def test_add_number_puts_exactly_one_digit(self):
        for _ in range(100):
            phrase = generate_passphrase(PassphraseOptions(add_number=True))
            self.assertEqual(sum(c.isdigit() for c in phrase), 1, phrase)

    def test_custom_wordlist(self):
        phrase = generate_passphrase(PassphraseOptions(words=4), wordlist=("sol", "mar"))
        self.assertTrue(set(phrase.split("-")) <= {"sol", "mar"})

    def test_phrases_are_not_repeated(self):
        phrases = {generate_passphrase() for _ in range(1000)}
        self.assertEqual(len(phrases), 1000)

    def test_invalid_options_raise(self):
        with self.assertRaises(ValueError):
            generate_passphrase(PassphraseOptions(words=MIN_WORDS - 1))
        with self.assertRaises(ValueError):
            generate_passphrase(PassphraseOptions(words=MAX_WORDS + 1))
        with self.assertRaises(ValueError):
            generate_passphrase(PassphraseOptions(separator="x"))
        with self.assertRaises(ValueError):
            generate_passphrase(wordlist=("solo",))


class PassphraseEntropyTests(unittest.TestCase):
    def test_entropy_six_words(self):
        n = len(load_wordlist())
        self.assertAlmostEqual(passphrase_entropy_bits(), 6 * math.log2(n))

    def test_number_adds_entropy(self):
        base = passphrase_entropy_bits(PassphraseOptions(words=6))
        with_num = passphrase_entropy_bits(PassphraseOptions(words=6, add_number=True))
        self.assertAlmostEqual(with_num - base, math.log2(10) + math.log2(6))

    def test_capitalize_adds_no_entropy(self):
        self.assertEqual(
            passphrase_entropy_bits(PassphraseOptions(capitalize=True)),
            passphrase_entropy_bits(PassphraseOptions()),
        )


if __name__ == "__main__":
    unittest.main()
