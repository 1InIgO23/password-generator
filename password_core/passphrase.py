"""Generación de frases de paso (estilo diceware).

Una frase de paso es una secuencia de palabras elegidas al azar de una
lista grande, por ejemplo: "lantern-oxidize-crumb-velvet-sprout-ample".
Es más fácil de recordar y teclear que "Z0rVJutPiBDC3FEN" y, con
suficientes palabras, igual de segura.

La lista por defecto es la "EFF Large Wordlist" (Electronic Frontier
Foundation, licencia CC BY 3.0): https://www.eff.org/dice
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
    capitalize: bool = False   # "Lantern-Oxidize-..." en lugar de "lantern-oxidize-..."
    add_number: bool = False   # añade un dígito al final de una palabra al azar


@lru_cache(maxsize=1)
def load_wordlist() -> tuple[str, ...]:
    """Carga la lista de palabras incluida en el paquete.

    Se cachea: el archivo se lee una sola vez aunque se generen muchas frases.
    Se descartan palabras con guion para que no se confundan con el separador.
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
        raise ValueError(f"El número de palabras debe estar entre {MIN_WORDS} y {MAX_WORDS}.")
    if len(wordlist) < 2:
        raise ValueError("La lista de palabras está vacía o es demasiado corta.")
    if any(c.isalpha() for c in opts.separator):
        raise ValueError("El separador no puede contener letras.")


def generate_passphrase(
    opts: PassphraseOptions = PassphraseOptions(),
    wordlist: tuple[str, ...] | None = None,
) -> str:
    """Genera una frase de paso según las opciones indicadas."""
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
    """Entropía en bits de una frase generada con estas opciones.

    Cada palabra aporta log2(tamaño de la lista) bits.
    El número opcional aporta log2(10) por el dígito + log2(palabras) por su posición.
    Mayúsculas y separador no aportan nada: siempre son iguales, el atacante los conoce.
    """
    wordlist = wordlist if wordlist is not None else load_wordlist()
    bits = opts.words * math.log2(len(wordlist))
    if opts.add_number:
        bits += math.log2(10) + math.log2(opts.words)
    return bits
