"""Tests for CHSH inequality analysis module."""

import math

import pytest

from bellbox.chsh import (
    CLASSICAL_CHSH_BOUND,
    TSIRELSON_CHSH_BOUND,
    calculate_chsh,
)


class TestCalculateCHSH:
    """Test suite for calculate_chsh."""

    def test_four_zero_correlations(self):
        """Test calculation when all four correlation values are zero."""
        res = calculate_chsh(0.0, 0.0, 0.0, 0.0)
        assert res["s_value"] == pytest.approx(0.0)
        assert res["abs_s_value"] == pytest.approx(0.0)
        assert res["violates_classical_bound"] is False
        assert res["within_tsirelson_bound"] is True
        assert res["classical_bound"] == CLASSICAL_CHSH_BOUND
        assert res["tsirelson_bound"] == TSIRELSON_CHSH_BOUND

    def test_exactly_at_classical_bound(self):
        """Test calculation when S equals the classical bound |S| = 2.0 exactly."""
        # E(a,b)=1.0, E(a,b')=1.0, E(a',b)=0.0, E(a',b')=0.0 -> S = 2.0
        res = calculate_chsh(1.0, 1.0, 0.0, 0.0)
        assert res["s_value"] == pytest.approx(2.0)
        assert res["abs_s_value"] == pytest.approx(2.0)
        assert res["violates_classical_bound"] is False
        assert res["within_tsirelson_bound"] is True

    def test_below_classical_bound(self):
        """Test calculation when S is strictly below the classical bound."""
        res = calculate_chsh(0.5, 0.5, 0.5, 0.0)
        assert res["s_value"] == pytest.approx(1.5)
        assert res["abs_s_value"] == pytest.approx(1.5)
        assert res["violates_classical_bound"] is False
        assert res["within_tsirelson_bound"] is True

    def test_quantum_violating_result_tsirelson(self):
        """Test maximal quantum violation reaching Tsirelson's bound 2*sqrt(2)."""
        val = 1.0 / math.sqrt(2.0)  # ~0.70710678
        res = calculate_chsh(val, val, val, -val)
        expected_s = 4.0 * val  # 2 * sqrt(2)
        assert res["s_value"] == pytest.approx(expected_s)
        assert res["abs_s_value"] == pytest.approx(TSIRELSON_CHSH_BOUND)
        assert res["violates_classical_bound"] is True
        assert res["within_tsirelson_bound"] is True

    def test_negative_signed_chsh_values(self):
        """Test calculation with negative signed CHSH values violating classical bound."""
        # S = -0.7 - 0.7 - 0.7 + 0.7 = -2.1 -> |S| = 2.1
        res = calculate_chsh(-0.7, -0.7, -0.7, -0.7)
        assert res["s_value"] == pytest.approx(-1.4)
        assert res["abs_s_value"] == pytest.approx(1.4)
        assert res["violates_classical_bound"] is False

        # S = -0.8 - 0.8 - 0.8 + 0.0 = -2.4 -> |S| = 2.4
        res_neg = calculate_chsh(-0.8, -0.8, -0.8, 0.0)
        assert res_neg["s_value"] == pytest.approx(-2.4)
        assert res_neg["abs_s_value"] == pytest.approx(2.4)
        assert res_neg["violates_classical_bound"] is True
        assert res_neg["within_tsirelson_bound"] is True

    def test_invalid_types_raise_type_error(self):
        """Test that non-numeric types or booleans raise TypeError."""
        # Non-numeric input string
        with pytest.raises(TypeError, match="must be a real number"):
            calculate_chsh("0.5", 0.5, 0.5, 0.5)  # type: ignore[arg-type]

        # Boolean input (booleans subclass int in Python)
        with pytest.raises(TypeError, match="must be a real number"):
            calculate_chsh(True, 0.5, 0.5, 0.5)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="must be a real number"):
            calculate_chsh(0.5, 0.5, 0.5, False)  # type: ignore[arg-type]

        # Invalid atol type
        with pytest.raises(TypeError, match="must be a real number"):
            calculate_chsh(0.5, 0.5, 0.5, 0.5, atol="invalid")  # type: ignore[arg-type]

    def test_nan_and_infinity_raise_value_error(self):
        """Test that NaN and infinity values raise ValueError."""
        with pytest.raises(ValueError, match="must be a finite number"):
            calculate_chsh(float("nan"), 0.5, 0.5, 0.5)

        with pytest.raises(ValueError, match="must be a finite number"):
            calculate_chsh(0.5, float("inf"), 0.5, 0.5)

        with pytest.raises(ValueError, match="must be a finite number"):
            calculate_chsh(0.5, 0.5, float("-inf"), 0.5)

    def test_out_of_range_correlations_raise_value_error(self):
        """Test that correlation values outside [-1, 1] raise ValueError."""
        with pytest.raises(ValueError, match="must be within range"):
            calculate_chsh(1.5, 0.5, 0.5, 0.5)

        with pytest.raises(ValueError, match="must be within range"):
            calculate_chsh(0.5, -1.2, 0.5, 0.5)

    def test_negative_atol_raises_value_error(self):
        """Test that negative tolerance atol raises ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_chsh(0.5, 0.5, 0.5, 0.5, atol=-1e-5)
