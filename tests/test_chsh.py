"""Tests for CHSH inequality analysis module."""

import math

import pytest
from qiskit.quantum_info import Statevector

from bellbox import phi_plus
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

    def test_individual_phi_plus_correlations_and_chsh_derivation(self):
        """Independently derive and check each of the 4 individual correlations for |Phi+>."""
        inv_sqrt2 = 1.0 / math.sqrt(2.0)

        # Theoretical quantum expectation for |Phi+> measured at angles (theta_A, theta_B):
        # E(theta_A, theta_B) = cos(theta_A - theta_B)
        # 1. E(a, b)   = cos(0 - pi/4)  = cos(-pi/4) = +1/sqrt(2)
        # 2. E(a, b')  = cos(0 - -pi/4) = cos(pi/4)  = +1/sqrt(2)
        # 3. E(a', b)  = cos(pi/2 - pi/4) = cos(pi/4) = +1/sqrt(2)
        # 4. E(a', b') = cos(pi/2 - -pi/4) = cos(3pi/4) = -1/sqrt(2)
        e_ab = math.cos(0.0 - math.pi / 4.0)
        e_ab_prime = math.cos(0.0 - (-math.pi / 4.0))
        e_a_prime_b = math.cos(math.pi / 2.0 - math.pi / 4.0)
        e_a_prime_b_prime = math.cos(math.pi / 2.0 - (-math.pi / 4.0))

        assert e_ab == pytest.approx(inv_sqrt2)
        assert e_ab_prime == pytest.approx(inv_sqrt2)
        assert e_a_prime_b == pytest.approx(inv_sqrt2)
        assert e_a_prime_b_prime == pytest.approx(-inv_sqrt2)

        res = calculate_chsh(e_ab, e_ab_prime, e_a_prime_b, e_a_prime_b_prime)
        assert res["s_value"] == pytest.approx(TSIRELSON_CHSH_BOUND)
        assert res["abs_s_value"] == pytest.approx(TSIRELSON_CHSH_BOUND)

    def test_qiskit_statevector_rotation_exact_quantum_correlations(self):
        """Verify Qiskit statevector basis rotations match exact analytical quantum correlations."""
        angles = [
            (0.0, math.pi / 4.0, 1.0 / math.sqrt(2.0)),
            (0.0, -math.pi / 4.0, 1.0 / math.sqrt(2.0)),
            (math.pi / 2.0, math.pi / 4.0, 1.0 / math.sqrt(2.0)),
            (math.pi / 2.0, -math.pi / 4.0, -1.0 / math.sqrt(2.0)),
        ]

        computed_corrs = []
        for ta, tb, expected_e in angles:
            qc = phi_plus()
            if ta != 0.0:
                qc.ry(-ta, 0)
            if tb != 0.0:
                qc.ry(-tb, 1)

            probs = Statevector(qc).probabilities_dict()
            # Calculate correlation E = P(00)+P(11)-P(01)-P(10) directly from exact probabilities
            p00 = probs.get("00", 0.0)
            p11 = probs.get("11", 0.0)
            p01 = probs.get("01", 0.0)
            p10 = probs.get("10", 0.0)
            e_val = (p00 + p11) - (p01 + p10)

            assert e_val == pytest.approx(expected_e, abs=1e-12)
            computed_corrs.append(e_val)

        chsh_res = calculate_chsh(*computed_corrs)
        assert chsh_res["s_value"] == pytest.approx(TSIRELSON_CHSH_BOUND, abs=1e-12)

    def test_setting_changes_and_sign_flips(self):
        """Verify CHSH parameter behavior when setting signs or order are varied."""
        val = 1.0 / math.sqrt(2.0)
        # Standard CHSH order: E(a,b) + E(a,b') + E(a',b) - E(a',b') = +2*sqrt(2)
        res_pos = calculate_chsh(val, val, val, -val)
        assert res_pos["s_value"] == pytest.approx(TSIRELSON_CHSH_BOUND)
        assert res_pos["abs_s_value"] == pytest.approx(TSIRELSON_CHSH_BOUND)

        # Flipped signs: E(a,b)=-val, E(a,b')=-val, E(a',b)=-val, E(a',b')=+val -> S = -2*sqrt(2)
        res_neg = calculate_chsh(-val, -val, -val, val)
        assert res_neg["s_value"] == pytest.approx(-TSIRELSON_CHSH_BOUND)
        assert res_neg["abs_s_value"] == pytest.approx(TSIRELSON_CHSH_BOUND)
        assert res_neg["violates_classical_bound"] is True
