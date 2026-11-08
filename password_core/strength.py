"""Estimación de fuerza de una contraseña generada aleatoriamente."""

from __future__ import annotations

import math


def entropy_bits(length: int, pool: int) -> float:
    """Entropía en bits de una cadena de `length` caracteres elegidos
    uniformemente de un conjunto de `pool` símbolos.

    Es una estimación: asume que la contraseña fue generada al azar.
    No sirve para evaluar contraseñas escritas por personas.
    """
    if length <= 0 or pool <= 1:
        return 0.0
    return length * math.log2(pool)


def strength_label(bits: float) -> str:
    """Etiqueta legible según la entropía en bits."""
    if bits < 40:
        return "Débil"
    if bits < 60:
        return "Razonable"
    if bits < 80:
        return "Fuerte"
    return "Muy segura"
