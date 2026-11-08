"""Strength estimation for randomly generated passwords."""

from __future__ import annotations

import math


def entropy_bits(length: int, pool: int) -> float:
    """Entropy in bits of a string of `length` characters chosen
    uniformly from a set of `pool` symbols.

    This is an estimate that assumes the password was generated at random.
    It is not suitable for evaluating passwords chosen by people.
    """
    if length <= 0 or pool <= 1:
        return 0.0
    return length * math.log2(pool)


def strength_label(bits: float) -> str:
    """Human-readable label based on entropy in bits."""
    if bits < 40:
        return "Débil"
    if bits < 60:
        return "Razonable"
    if bits < 80:
        return "Fuerte"
    return "Muy segura"
