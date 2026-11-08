"""Random password generation using the operating system's CSPRNG.

All randomness comes from `secrets` (backed by os.urandom).
Never use `random` for anything generated here.
"""

from __future__ import annotations

import secrets
import string
from dataclasses import dataclass

MIN_LENGTH = 4
MAX_LENGTH = 128

UPPER = string.ascii_uppercase
LOWER = string.ascii_lowercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>?"

# Characters that are easily confused when reading or typing.
AMBIGUOUS = frozenset("0O1lI")


@dataclass(frozen=True)
class Options:
    length: int = 16
    upper: bool = True
    lower: bool = True
    digits: bool = True
    symbols: bool = False
    exclude_ambiguous: bool = False


def _character_classes(opts: Options) -> list[str]:
    """Return one string per enabled character class."""
    selected = []
    if opts.upper:
        selected.append(UPPER)
    if opts.lower:
        selected.append(LOWER)
    if opts.digits:
        selected.append(DIGITS)
    if opts.symbols:
        selected.append(SYMBOLS)

    if opts.exclude_ambiguous:
        selected = ["".join(c for c in cls if c not in AMBIGUOUS) for cls in selected]

    return [cls for cls in selected if cls]


def _validate(opts: Options) -> list[str]:
    classes = _character_classes(opts)
    if not classes:
        raise ValueError("Select at least one character set.")
    if not MIN_LENGTH <= opts.length <= MAX_LENGTH:
        raise ValueError(
            f"Length must be between {MIN_LENGTH} and {MAX_LENGTH}."
        )
    if opts.length < len(classes):
        raise ValueError(
            f"Length ({opts.length}) cannot be less than the number "
            f"of selected character sets ({len(classes)})."
        )
    return classes


def pool_size(opts: Options) -> int:
    """Number of distinct characters that can be picked from."""
    return sum(len(cls) for cls in _character_classes(opts))


def generate_password(opts: Options = Options()) -> str:
    """Generate a password that satisfies the given options.

    Guarantees at least one character from each selected class.
    """
    classes = _validate(opts)
    pool = "".join(classes)

    # One character from each enabled class, to meet the guarantee...
    chars = [secrets.choice(cls) for cls in classes]
    # ...and the rest come from the full pool.
    chars += [secrets.choice(pool) for _ in range(opts.length - len(chars))]

    # Shuffle so the guaranteed positions are not predictable.
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)
