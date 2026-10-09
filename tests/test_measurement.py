"""Tests for measurement utilities and probability distribution normalization."""

import pytest

from bellbox.measurement import analyze_counts, counts_to_probabilities, is_normalized


class TestAnalyzeCounts:
    """Test suite for analyze_counts."""

    def test_normal_distribution(self):
        """Test analysis of a typical measurement count distribution."""
        counts = {"00": 510, "11": 490}
        res = analyze_counts(counts)
        assert res["total_shots"] == 1000
        assert res["probabilities"]["00"] == pytest.approx(0.51)
        assert res["probabilities"]["11"] == pytest.approx(0.49)
        assert is_normalized(res["probabilities"])

    def test_single_outcome(self):
        """Test analysis when all measurement shots yield a single outcome."""
        counts = {"00": 100}
        res = analyze_counts(counts)
        assert res["total_shots"] == 100
        assert res["probabilities"] == {"00": 1.0}
        assert is_normalized(res["probabilities"])

    def test_multiple_outcomes_different_probabilities(self):
        """Test analysis with multiple outcomes, unequal counts, and key sorting."""
        counts = {"11": 300, "00": 100, "01": 600}
        res = analyze_counts(counts)
        assert res["total_shots"] == 1000
        assert list(res["probabilities"].keys()) == ["00", "01", "11"]
        assert res["probabilities"]["00"] == pytest.approx(0.1)
        assert res["probabilities"]["01"] == pytest.approx(0.6)
        assert res["probabilities"]["11"] == pytest.approx(0.3)
        assert is_normalized(res["probabilities"])

    def test_empty_counts(self):
        """Test that empty dictionary returns total_shots 0 and empty probabilities."""
        res = analyze_counts({})
        assert res == {"total_shots": 0, "probabilities": {}}

    def test_individual_zero_count_with_non_zero_total(self):
        """Test when individual outcomes have 0 counts but total shots > 0."""
        counts = {"00": 100, "11": 0}
        res = analyze_counts(counts)
        assert res["total_shots"] == 100
        assert res["probabilities"]["00"] == pytest.approx(1.0)
        assert res["probabilities"]["11"] == pytest.approx(0.0)

    def test_zero_total_counts_raises_value_error(self):
        """Test that counts summing to zero in a non-empty mapping raise ValueError."""
        with pytest.raises(ValueError, match="Total measurement count is zero"):
            analyze_counts({"00": 0, "11": 0})

    def test_negative_counts_raises_value_error(self):
        """Test that negative count values raise ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            analyze_counts({"00": -10, "11": 100})

    def test_float_counts_raises_type_error(self):
        """Test that float count values raise TypeError."""
        with pytest.raises(TypeError, match="must be an integer"):
            analyze_counts({"00": 5.5, "11": 10})  # type: ignore[dict-item]

    def test_boolean_counts_raises_type_error(self):
        """Test that boolean count values raise TypeError."""
        with pytest.raises(TypeError, match="must be an integer"):
            analyze_counts({"00": True, "11": False})  # type: ignore[dict-item]

    def test_non_string_key_raises_type_error(self):
        """Test that non-string bitstring keys raise TypeError."""
        with pytest.raises(TypeError, match="Bitstring key must be a string"):
            analyze_counts({0: 50, 1: 50})  # type: ignore[dict-item]

    def test_invalid_bitstring_chars_raises_value_error(self):
        """Test that non-binary bitstring characters raise ValueError."""
        with pytest.raises(ValueError, match="Invalid bitstring key"):
            analyze_counts({"02": 50, "11": 50})

        with pytest.raises(ValueError, match="Invalid bitstring key"):
            analyze_counts({"abc": 50})

    def test_inconsistent_bitstring_lengths_raises_value_error(self):
        """Test that bitstring keys of differing lengths raise ValueError."""
        with pytest.raises(ValueError, match="Inconsistent bitstring length"):
            analyze_counts({"00": 50, "111": 50})

    def test_non_mapping_input_raises_type_error(self):
        """Test that non-mapping input raises TypeError."""
        with pytest.raises(TypeError, match="must be a dictionary-like mapping"):
            analyze_counts([("00", 50), ("11", 50)])  # type: ignore[arg-type]


class TestCountsToProbabilities:
    """Test suite for counts_to_probabilities."""

    def test_valid_counts_conversion(self):
        """Test normalization of valid measurement counts."""
        counts = {"00": 500, "11": 500}
        probs = counts_to_probabilities(counts)
        assert probs == {"00": 0.5, "11": 0.5}
        assert is_normalized(probs)

    def test_asymmetric_counts_conversion(self):
        """Test normalization of unequal shot counts and output key sorting."""
        # Intentionally pass keys out of order
        counts = {"11": 300, "00": 100, "01": 600}
        probs = counts_to_probabilities(counts)
        assert list(probs.keys()) == ["00", "01", "11"]
        assert probs["00"] == pytest.approx(0.1)
        assert probs["01"] == pytest.approx(0.6)
        assert probs["11"] == pytest.approx(0.3)
        assert is_normalized(probs)

    def test_empty_counts_returns_empty_dict(self):
        """Test that empty dictionary input returns an empty dictionary."""
        assert counts_to_probabilities({}) == {}

    def test_zero_total_counts_raises_value_error(self):
        """Test that counts summing to zero raise a ValueError."""
        with pytest.raises(ValueError, match="Total measurement count is zero"):
            counts_to_probabilities({"00": 0, "11": 0})

    def test_negative_counts_raises_value_error(self):
        """Test that negative counts raise a ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            counts_to_probabilities({"00": -10, "11": 100})

    def test_float_counts_raises_type_error(self):
        """Test that float count values raise a TypeError."""
        with pytest.raises(TypeError, match="must be an integer"):
            counts_to_probabilities({"00": 5.5, "11": 10})  # type: ignore[dict-item]

    def test_boolean_counts_raises_type_error(self):
        """Test that boolean count values raise a TypeError."""
        with pytest.raises(TypeError, match="must be an integer"):
            counts_to_probabilities({"00": True, "11": False})  # type: ignore[dict-item]

    def test_non_string_key_raises_type_error(self):
        """Test that non-string bitstring keys raise a TypeError."""
        with pytest.raises(TypeError, match="Bitstring key must be a string"):
            counts_to_probabilities({0: 50, 1: 50})  # type: ignore[dict-item]

    def test_invalid_bitstring_chars_raises_value_error(self):
        """Test that non-binary bitstring characters raise a ValueError."""
        with pytest.raises(ValueError, match="Invalid bitstring key"):
            counts_to_probabilities({"02": 50, "11": 50})

        with pytest.raises(ValueError, match="Invalid bitstring key"):
            counts_to_probabilities({"abc": 50})

    def test_non_mapping_input_raises_type_error(self):
        """Test that non-mapping input raises a TypeError."""
        with pytest.raises(TypeError, match="must be a dictionary-like mapping"):
            counts_to_probabilities([("00", 50), ("11", 50)])  # type: ignore[arg-type]


class TestIsNormalized:
    """Test suite for is_normalized."""

    def test_valid_normalized_distribution(self):
        """Test properly normalized distributions return True."""
        assert is_normalized({"00": 0.5, "11": 0.5}) is True
        assert is_normalized({"0": 1.0}) is True

    def test_unnormalized_distribution_returns_false(self):
        """Test distributions that do not sum to 1.0 return False."""
        assert is_normalized({"00": 0.5, "11": 0.6}) is False
        assert is_normalized({"00": 0.3, "11": 0.3}) is False

    def test_probability_out_of_range_returns_false(self):
        """Test probabilities > 1 or < 0 return False."""
        assert is_normalized({"00": 1.2, "11": -0.2}) is False
        assert is_normalized({"00": -0.05, "11": 1.05}) is False

    def test_empty_distribution_returns_false(self):
        """Test empty distribution returns False."""
        assert is_normalized({}) is False

    def test_tolerance_parameter(self):
        """Test behavior near boundary with custom atol."""
        probs = {"00": 0.500001, "11": 0.5}
        assert is_normalized(probs, atol=1e-5) is True
        assert is_normalized(probs, atol=1e-8) is False

    def test_nan_or_inf_returns_false(self):
        """Test NaN or Infinity values return False."""
        assert is_normalized({"00": float("nan"), "11": 0.5}) is False
        assert is_normalized({"00": float("inf"), "11": 0.5}) is False

    def test_invalid_atol_type_or_value(self):
        """Test invalid tolerance arguments raise exceptions."""
        with pytest.raises(TypeError, match="must be a real number"):
            is_normalized({"00": 0.5, "11": 0.5}, atol="invalid")  # type: ignore[arg-type]

        with pytest.raises(ValueError, match="cannot be negative"):
            is_normalized({"00": 0.5, "11": 0.5}, atol=-1e-5)

    def test_invalid_input_types_raise_exceptions(self):
        """Test non-mapping or invalid key/value types raise exceptions."""
        with pytest.raises(TypeError, match="must be a dictionary-like mapping"):
            is_normalized(None)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Bitstring key must be a string"):
            is_normalized({0: 0.5, 1: 0.5})  # type: ignore[dict-item]

        with pytest.raises(TypeError, match="must be a number"):
            is_normalized({"00": "0.5", "11": "0.5"})  # type: ignore[dict-item]
