import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from bellbox.measurement import (
    analyze_counts,
    calculate_correlations,
    counts_to_probabilities,
    is_normalized,
    measure_in_basis,
)
from bellbox.states import phi_plus


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


class TestCalculateCorrelations:
    """Test suite for calculate_correlations."""

    def test_perfect_positive_correlation(self):
        """Test perfect positive correlation where all outcomes are agreeing (00, 11)."""
        counts = {"00": 50, "11": 50}
        res = calculate_correlations(counts)
        assert res["total_shots"] == 100
        assert res["agree_count"] == 100
        assert res["agree_probability"] == pytest.approx(1.0)
        assert res["differ_count"] == 0
        assert res["differ_probability"] == pytest.approx(0.0)
        assert res["correlation"] == pytest.approx(1.0)

    def test_perfect_negative_correlation(self):
        """Test perfect negative correlation where all outcomes are differing (01, 10)."""
        counts = {"01": 50, "10": 50}
        res = calculate_correlations(counts)
        assert res["total_shots"] == 100
        assert res["agree_count"] == 0
        assert res["agree_probability"] == pytest.approx(0.0)
        assert res["differ_count"] == 100
        assert res["differ_probability"] == pytest.approx(1.0)
        assert res["correlation"] == pytest.approx(-1.0)

    def test_mixed_distribution_all_outcomes(self):
        """Test a mixed distribution containing all four two-qubit outcomes."""
        counts = {"00": 40, "01": 10, "10": 20, "11": 30}
        res = calculate_correlations(counts)
        assert res["total_shots"] == 100
        assert res["agree_count"] == 70
        assert res["agree_probability"] == pytest.approx(0.7)
        assert res["differ_count"] == 30
        assert res["differ_probability"] == pytest.approx(0.3)
        assert res["correlation"] == pytest.approx(0.4)

    def test_single_observed_outcome(self):
        """Test distribution where only a single outcome is observed."""
        counts = {"00": 100}
        res = calculate_correlations(counts)
        assert res["total_shots"] == 100
        assert res["agree_count"] == 100
        assert res["agree_probability"] == pytest.approx(1.0)
        assert res["differ_count"] == 0
        assert res["differ_probability"] == pytest.approx(0.0)
        assert res["correlation"] == pytest.approx(1.0)

    def test_unequal_counts(self):
        """Test analysis with unequal counts across outcomes."""
        counts = {"00": 10, "01": 30, "11": 60}
        res = calculate_correlations(counts)
        assert res["total_shots"] == 100
        assert res["agree_count"] == 70
        assert res["agree_probability"] == pytest.approx(0.7)
        assert res["differ_count"] == 30
        assert res["differ_probability"] == pytest.approx(0.3)
        assert res["correlation"] == pytest.approx(0.4)

    def test_missing_outcomes(self):
        """Test that missing outcomes default to zero count without error."""
        counts = {"11": 80}
        res = calculate_correlations(counts)
        assert res["total_shots"] == 80
        assert res["agree_count"] == 80
        assert res["agree_probability"] == pytest.approx(1.0)
        assert res["differ_count"] == 0
        assert res["differ_probability"] == pytest.approx(0.0)
        assert res["correlation"] == pytest.approx(1.0)

    def test_empty_and_zero_total_inputs(self):
        """Test empty mapping and zero total shot inputs."""
        empty_res = calculate_correlations({})
        assert empty_res["total_shots"] == 0
        assert empty_res["agree_count"] == 0
        assert empty_res["agree_probability"] == pytest.approx(0.0)
        assert empty_res["differ_count"] == 0
        assert empty_res["differ_probability"] == pytest.approx(0.0)
        assert empty_res["correlation"] == pytest.approx(0.0)

        with pytest.raises(ValueError, match="Total measurement count is zero"):
            calculate_correlations({"00": 0, "11": 0})

    def test_invalid_bitstrings_and_count_values(self):
        """Test exceptions raised for invalid bitstrings and count values."""
        # Non-mapping input
        with pytest.raises(TypeError, match="must be a dictionary-like mapping"):
            calculate_correlations([("00", 50)])  # type: ignore[arg-type]

        # Non-string key
        with pytest.raises(TypeError, match="Bitstring key must be a string"):
            calculate_correlations({0: 50})  # type: ignore[dict-item]

        # Non-binary key characters
        with pytest.raises(ValueError, match="Invalid bitstring key"):
            calculate_correlations({"02": 50})

        # Length other than 2
        with pytest.raises(ValueError, match="must have length 2"):
            calculate_correlations({"0": 50})

        with pytest.raises(ValueError, match="must have length 2"):
            calculate_correlations({"000": 50})

        # Non-integer / boolean count
        with pytest.raises(TypeError, match="must be an integer"):
            calculate_correlations({"00": 5.5})  # type: ignore[dict-item]

        with pytest.raises(TypeError, match="must be an integer"):
            calculate_correlations({"00": True})  # type: ignore[dict-item]

        # Negative count
        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_correlations({"00": -10})


class TestMeasureInBasis:
    """Test suite for measure_in_basis."""

    def test_z_basis_measurement(self):
        """Test computational (Z) basis measurement adds no rotation gates."""
        qc = phi_plus()
        qc_meas = measure_in_basis(qc, "Z")
        op_names = [inst.operation.name for inst in qc_meas.data]
        assert op_names.count("h") == 1  # 1 from phi_plus, 0 added by Z-basis
        assert "sdg" not in op_names
        assert "measure" in op_names

    def test_x_basis_measurement(self):
        """Test X basis measurement applies Hadamard (h) gates before measurement."""
        qc = phi_plus()
        qc_meas = measure_in_basis(qc, "X")
        op_names = [inst.operation.name for inst in qc_meas.data]
        assert op_names.count("h") == 3  # 1 from phi_plus, 2 from X-basis
        assert "sdg" not in op_names
        assert "measure" in op_names

    def test_y_basis_measurement(self):
        """Test Y basis measurement applies sdg then h gates before measurement."""
        qc = phi_plus()
        qc_meas = measure_in_basis(qc, "Y")
        op_names = [inst.operation.name for inst in qc_meas.data]
        assert op_names.count("sdg") == 2
        assert op_names.count("h") == 3  # 1 from phi_plus, 2 from Y-basis
        assert "measure" in op_names

    def test_per_qubit_basis_sequence(self):
        """Test specifying different bases per qubit (e.g. XZ and ['Y', 'X'])."""
        qc = phi_plus()
        qc_xz = measure_in_basis(qc, "XZ")
        ops_q0 = [
            inst.operation.name
            for inst in qc_xz.data
            if 0 in [qc_xz.find_bit(q).index for q in inst.qubits]
        ]
        ops_q1 = [
            inst.operation.name
            for inst in qc_xz.data
            if 1 in [qc_xz.find_bit(q).index for q in inst.qubits]
        ]
        assert ops_q0.count("h") == 2  # 1 from phi_plus + 1 from X-basis
        assert ops_q1.count("h") == 0  # Z-basis adds no H

        qc_yx = measure_in_basis(qc, ["Y", "X"])
        assert "sdg" in [inst.operation.name for inst in qc_yx.data]

    def test_circuit_preservation_and_mutation(self):
        """Test default non-destructive copying (inplace=False) and mutation (inplace=True)."""
        qc_orig = phi_plus()
        num_gates_orig = len(qc_orig.data)

        # Default inplace=False preserves original circuit
        qc_copy = measure_in_basis(qc_orig, "X", inplace=False)
        assert qc_copy is not qc_orig
        assert len(qc_orig.data) == num_gates_orig
        assert not any(inst.operation.name == "measure" for inst in qc_orig.data)
        assert any(inst.operation.name == "measure" for inst in qc_copy.data)

        # inplace=True mutates original circuit
        qc_mutated = measure_in_basis(qc_orig, "X", inplace=True)
        assert qc_mutated is qc_orig
        assert any(inst.operation.name == "measure" for inst in qc_orig.data)

    def test_deterministic_quantum_state_basis_rotations(self):
        """Test deterministic quantum probabilities of |Phi+> under Z, X, Y basis rotations."""
        qc = phi_plus()

        # Z-basis statevector probabilities before measure gate
        sv_z = Statevector(qc)
        probs_z = sv_z.probabilities_dict()
        assert probs_z["00"] == pytest.approx(0.5)
        assert probs_z["11"] == pytest.approx(0.5)

        # X-basis rotation H x H on |Phi+> leaves state invariant: 0.5 |00> + 0.5 |11>
        qc_x = qc.copy()
        qc_x.h(0)
        qc_x.h(1)
        probs_x = Statevector(qc_x).probabilities_dict()
        assert probs_x["00"] == pytest.approx(0.5)
        assert probs_x["11"] == pytest.approx(0.5)

        # Y-basis rotation (H S^dag) x (H S^dag) on |Phi+> yields |Psi+>: 0.5 |01> + 0.5 |10>
        qc_y = qc.copy()
        qc_y.sdg(0)
        qc_y.h(0)
        qc_y.sdg(1)
        qc_y.h(1)
        probs_y = Statevector(qc_y).probabilities_dict()
        assert probs_y["01"] == pytest.approx(0.5)
        assert probs_y["10"] == pytest.approx(0.5)

    def test_invalid_inputs_raise_exceptions(self):
        """Test invalid arguments raise appropriate TypeError or ValueError exceptions."""
        qc = phi_plus()

        # Non-QuantumCircuit input
        with pytest.raises(TypeError, match="Expected a Qiskit QuantumCircuit"):
            measure_in_basis("not_a_circuit")  # type: ignore[arg-type]

        # Non-boolean inplace
        with pytest.raises(TypeError, match="Expected bool for inplace"):
            measure_in_basis(qc, "X", inplace="yes")  # type: ignore[arg-type]

        # Invalid basis character
        with pytest.raises(ValueError, match="Invalid measurement basis"):
            measure_in_basis(qc, "W")

        # Invalid basis length
        with pytest.raises(ValueError, match="Invalid basis string length"):
            measure_in_basis(qc, "XXX")

        with pytest.raises(ValueError, match="Basis sequence length"):
            measure_in_basis(qc, ["X"])

        # Non-string in basis sequence
        with pytest.raises(TypeError, match="Basis element must be a string"):
            measure_in_basis(qc, ["X", 123])  # type: ignore[list-item]

        # Circuit with 0 qubits
        with pytest.raises(ValueError, match="0 qubits"):
            measure_in_basis(QuantumCircuit(0))

        # Circuit already containing measurement operations
        qc_measured = measure_in_basis(qc, "Z")
        with pytest.raises(ValueError, match="already contains measurement operations"):
            measure_in_basis(qc_measured, "X")


