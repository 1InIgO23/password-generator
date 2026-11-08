"""Passphrase generation (diceware style).

A passphrase is a sequence of words chosen at random from a large list,
for example: "lantern-oxidize-crumb-velvet-sprout-ample".
It is easier to remember and type than "Z0rVJutPiBDC3FEN" and, with
enough words, just as secure.

The default list is the EFF Large Wordlist (Electronic Frontier
Foundation, CC BY 3.0 license): https://www.eff.org/dice
"""

from __future__ import annotations

import math
import secrets
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources

MIN_WORDS = 3
MAX_WORDS = 20


@dataclass(frozen=True)
class PassphraseOptions:
    words: int = 6
    separator: str = "-"
    capitalize: bool = False   # "Lantern-Oxidize-..." instead of "lantern-oxidize-..."
    add_number: bool = False   # append one digit to the end of a random word


@lru_cache(maxsize=1)
def load_wordlist() -> tuple[str, ...]:
    """Load the wordlist bundled with the package.

    Cached: the file is read only once, however many phrases are generated.
    Hyphenated words are dropped so they can't be confused with the separator.
    """
    text = (
        resources.files("password_core")
        .joinpath("wordlists/eff_large.txt")
        .read_text(encoding="utf-8")
    )
    words = {w.strip().lower() for w in text.split()}
    return tuple(sorted(w for w in words if w.isalpha()))


def _validate(opts: PassphraseOptions, wordlist: tuple[str, ...]) -> None:
    if not MIN_WORDS <= opts.words <= MAX_WORDS:
        raise ValueError(f"Number of words must be between {MIN_WORDS} and {MAX_WORDS}.")
    if len(wordlist) < 2:
        raise ValueError("The wordlist is empty or too short.")
    if any(c.isalpha() for c in opts.separator):
        raise ValueError("The separator cannot contain letters.")


def generate_passphrase(
    opts: PassphraseOptions = PassphraseOptions(),
    wordlist: tuple[str, ...] | None = None,
) -> str:
    """Generate a passphrase according to the given options."""
    wordlist = wordlist if wordlist is not None else load_wordlist()
    _validate(opts, wordlist)

    words = [secrets.choice(wordlist) for _ in range(opts.words)]

    if opts.capitalize:
        words = [w.capitalize() for w in words]

    if opts.add_number:
        i = secrets.randbelow(len(words))
        words[i] += str(secrets.randbelow(10))

    return opts.separator.join(words)


def passphrase_entropy_bits(
    opts: PassphraseOptions = PassphraseOptions(),
    wordlist: tuple[str, ...] | None = None,
) -> float:
    """Entropy in bits of a phrase generated with these options.

    Each word contributes log2(wordlist size) bits.
    The optional number adds log2(10) for the digit + log2(words) for its position.
    Capitalization and separator add nothing: they are always the same,
    so an attacker already knows them.
    """
    wordlist = wordlist if wordlist is not None else load_wordlist()
    bits = opts.words * math.log2(len(wordlist))
    if opts.add_number:
        bits += math.log2(10) + math.log2(opts.words)
    return bits
