"""Utilities for analyzing quantum measurement results and probability distributions.

This module provides tools to convert raw measurement counts (shot counts) into
normalized probability distributions and to validate distribution properties.
"""

import math
from collections.abc import Mapping


def counts_to_probabilities(counts: Mapping[str, int]) -> dict[str, float]:
    """Convert quantum measurement outcome counts into normalized probabilities.

    Args:
        counts: A dictionary-like mapping of bitstrings (e.g. '00', '01')
            to non-negative integer shot counts.

    Returns:
        dict[str, float]: A dictionary mapping each bitstring to its estimated probability,
            sorted alphabetically by bitstring key. Returns an empty dictionary if input
            counts is empty.

    Raises:
        TypeError: If `counts` is not a Mapping, if any key is not a string,
            or if any count is not an integer.
        ValueError: If any bitstring contains characters other than '0' or '1',
            if any count is negative, or if total counts sum to zero.

    Bitstring and Output Ordering:
        Bitstrings in Qiskit follow little-endian ordering by convention
        (qubit n-1 ... qubit 0). The returned dictionary keys are sorted
        lexicographically to ensure deterministic iteration order regardless of input dict order.
    """
    if not isinstance(counts, Mapping):
        raise TypeError(f"Counts must be a dictionary-like mapping, got {type(counts).__name__}.")

    if not counts:
        return {}

    total_shots = 0
    validated_counts: list[tuple[str, int]] = []

    for bitstring, count in counts.items():
        if not isinstance(bitstring, str):
            raise TypeError(
                f"Bitstring key must be a string, got {type(bitstring).__name__}: {bitstring!r}."
            )

        if not bitstring or any(char not in ("0", "1") for char in bitstring):
            raise ValueError(f"Invalid bitstring key {bitstring!r}: must contain only '0' and '1'.")

        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError(
                f"Count for bitstring {bitstring!r} must be an integer, got {type(count).__name__}."
            )

        if count < 0:
            raise ValueError(f"Count for bitstring {bitstring!r} cannot be negative, got {count}.")

        total_shots += count
        validated_counts.append((bitstring, count))

    if total_shots == 0:
        raise ValueError("Total measurement count is zero; cannot normalize probabilities.")

    # Sort lexicographically by bitstring key
    validated_counts.sort(key=lambda item: item[0])

    return {bitstring: count / total_shots for bitstring, count in validated_counts}


def is_normalized(
    probabilities: Mapping[str, float],
    atol: float = 1e-6,
) -> bool:
    """Validate whether a probability distribution is properly normalized.

    A distribution is normalized if all probabilities are within [0, 1] (up to tolerance)
    and their sum equals 1.0 within tolerance.

    Args:
        probabilities: A dictionary-like mapping of bitstrings to float probabilities.
        atol: Absolute numerical tolerance for probability bounds and sum check (default: 1e-6).

    Returns:
        bool: True if probabilities sum to approximately 1.0 and each probability is in [0, 1],
            False otherwise (including empty distributions).

    Raises:
        TypeError: If `probabilities` is not a Mapping, if any key is not a string,
            if any probability is not a real number, or if atol is not a non-negative float.
        ValueError: If any bitstring key is invalid or if atol is negative.
    """
    if not isinstance(probabilities, Mapping):
        raise TypeError(
            f"Probabilities must be a dictionary-like mapping, got {type(probabilities).__name__}."
        )

    if isinstance(atol, bool) or not isinstance(atol, (int, float)):
        raise TypeError(f"Tolerance atol must be a real number, got {type(atol).__name__}.")

    if atol < 0:
        raise ValueError(f"Tolerance atol cannot be negative, got {atol}.")

    if not probabilities:
        return False

    total_prob = 0.0

    for bitstring, prob in probabilities.items():
        if not isinstance(bitstring, str):
            raise TypeError(
                f"Bitstring key must be a string, got {type(bitstring).__name__}: {bitstring!r}."
            )

        if not bitstring or any(char not in ("0", "1") for char in bitstring):
            raise ValueError(f"Invalid bitstring key {bitstring!r}: must contain only '0' and '1'.")

        if isinstance(prob, bool) or not isinstance(prob, (int, float)):
            raise TypeError(
                f"Probability for bitstring {bitstring!r} must be a number, "
                f"got {type(prob).__name__}."
            )

        if math.isnan(prob) or math.isinf(prob):
            return False

        if prob < -atol or prob > (1.0 + atol):
            return False

        total_prob += prob

    return abs(total_prob - 1.0) <= atol
