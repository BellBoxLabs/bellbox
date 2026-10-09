"""Clauser-Horne-Shimony-Holt (CHSH) Bell inequality analysis module.

This module provides tools for calculating and analyzing CHSH inequality statistics
from correlation values across four measurement setting pairs: (a, b), (a, b'), (a', b), (a', b').

Mathematical Background:
    The CHSH correlation inequality test evaluates the statistic:
        S = E(a, b) + E(a, b') + E(a', b) - E(a', b')

    - Classical Local Realism Bound: |S| <= 2.0
    - Quantum Tsirelson's Bound:     |S| <= 2 * sqrt(2) ~ 2.828427...

IMPORTANT SCIENTIFIC DISCLAIMER:
    Evaluating S mathematically from given correlation values calculates whether those specific
    correlations violate local realism. A violation in an ideal numerical or simulated experiment
    demonstrates theoretical quantum predictions, but does NOT constitute physical experimental
    proof, which requires physical hardware, detector efficiency calibration, and statistical error
    analysis.
"""

import math
from typing import Any

CLASSICAL_CHSH_BOUND: float = 2.0
TSIRELSON_CHSH_BOUND: float = 2.0 * math.sqrt(2.0)  # ~2.8284271247461903


def calculate_chsh(
    e_ab: float,
    e_ab_prime: float,
    e_a_prime_b: float,
    e_a_prime_b_prime: float,
    atol: float = 1e-6,
) -> dict[str, Any]:
    """Calculate the CHSH Bell inequality statistic S and evaluate classical/quantum bounds.

    Given four correlation values E(a, b), E(a, b'), E(a', b), E(a', b') for measurement settings
    a, a' (Alice) and b, b' (Bob), computes the CHSH correlation parameter:

        S = E(a, b) + E(a, b') + E(a', b) - E(a', b')

    Args:
        e_ab: Correlation E(a, b) for settings (a, b). Must be in [-1, 1].
        e_ab_prime: Correlation E(a, b') for settings (a, b'). Must be in [-1, 1].
        e_a_prime_b: Correlation E(a', b) for settings (a', b). Must be in [-1, 1].
        e_a_prime_b_prime: Correlation E(a', b') for settings (a', b'). Must be in [-1, 1].
        atol: Absolute numerical tolerance for bound checks and range validation (default: 1e-6).

    Returns:
        dict[str, Any]: A dictionary containing CHSH analysis results:
            - 's_value' (float): Signed CHSH statistic S.
            - 'abs_s_value' (float): Absolute magnitude |S|.
            - 'classical_bound' (float): The classical local-realist bound (2.0).
            - 'tsirelson_bound' (float): Tsirelson's maximum quantum bound (~2.8284).
            - 'violates_classical_bound' (bool): True if |S| > 2.0 + atol.
            - 'within_tsirelson_bound' (bool): True if |S| <= 2 * sqrt(2) + atol.
            - 'correlations' (dict[str, float]): Dictionary mirroring input correlations.

    Raises:
        TypeError: If any input correlation or atol is not a real number (or is a boolean).
        ValueError: If atol is negative, or if any correlation value is NaN, infinite, or outside
            the range [-1, 1].
    """
    if isinstance(atol, bool) or not isinstance(atol, (int, float)):
        raise TypeError(f"Tolerance atol must be a real number, got {type(atol).__name__}.")

    if atol < 0:
        raise ValueError(f"Tolerance atol cannot be negative, got {atol}.")

    correlations_dict = {
        "e_ab": e_ab,
        "e_ab_prime": e_ab_prime,
        "e_a_prime_b": e_a_prime_b,
        "e_a_prime_b_prime": e_a_prime_b_prime,
    }

    for name, val in correlations_dict.items():
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            raise TypeError(
                f"Correlation {name!r} must be a real number, got {type(val).__name__}."
            )

        val_float = float(val)

        if math.isnan(val_float) or math.isinf(val_float):
            raise ValueError(f"Correlation {name!r} must be a finite number, got {val}.")

        if val_float < (-1.0 - atol) or val_float > (1.0 + atol):
            raise ValueError(
                f"Correlation {name!r} must be within range [-1.0, 1.0], got {val}."
            )

    s_val = float(e_ab) + float(e_ab_prime) + float(e_a_prime_b) - float(e_a_prime_b_prime)
    abs_s_val = abs(s_val)

    violates_classical = abs_s_val > (CLASSICAL_CHSH_BOUND + atol)
    within_tsirelson = abs_s_val <= (TSIRELSON_CHSH_BOUND + atol)

    return {
        "s_value": s_val,
        "abs_s_value": abs_s_val,
        "classical_bound": CLASSICAL_CHSH_BOUND,
        "tsirelson_bound": TSIRELSON_CHSH_BOUND,
        "violates_classical_bound": violates_classical,
        "within_tsirelson_bound": within_tsirelson,
        "correlations": {k: float(v) for k, v in correlations_dict.items()},
    }
