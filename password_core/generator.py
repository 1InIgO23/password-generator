"""Generación de contraseñas aleatorias usando el CSPRNG del sistema.

Toda la aleatoriedad proviene de `secrets` (os.urandom por debajo).
No usar `random` para nada de lo que aquí se genera.
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

# Caracteres que se confunden fácilmente al leerlos o escribirlos.
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
    """Devuelve una cadena por cada clase de caracteres activa."""
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
        raise ValueError("Hay que seleccionar al menos un juego de caracteres.")
    if not MIN_LENGTH <= opts.length <= MAX_LENGTH:
        raise ValueError(
            f"La longitud debe estar entre {MIN_LENGTH} y {MAX_LENGTH}."
        )
    if opts.length < len(classes):
        raise ValueError(
            f"La longitud ({opts.length}) no puede ser menor que el número "
            f"de juegos de caracteres seleccionados ({len(classes)})."
        )
    return classes


def pool_size(opts: Options) -> int:
    """Número de caracteres distintos entre los que se puede elegir."""
    return sum(len(cls) for cls in _character_classes(opts))


def generate_password(opts: Options = Options()) -> str:
    """Genera una contraseña que cumple las opciones indicadas.

    Garantiza al menos un carácter de cada clase seleccionada.
    """
    classes = _validate(opts)
    pool = "".join(classes)

    # Un carácter de cada clase activa, para cumplir la garantía...
    chars = [secrets.choice(cls) for cls in classes]
    # ...y el resto sale del conjunto completo.
    chars += [secrets.choice(pool) for _ in range(opts.length - len(chars))]

    # Mezclar para que las posiciones obligatorias no sean predecibles.
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)
