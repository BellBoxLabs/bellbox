"""Tests for circuit property validation utilities."""

import pytest
from qiskit import QuantumCircuit

from bellbox.states import phi_plus
from bellbox.validation import (
    has_measurements,
    validate_circuit,
    validate_qubit_count,
)


class TestValidateQubitCount:
    """Test suite for validate_qubit_count."""

    def test_matching_qubit_count(self):
        """Test returning True when qubit count matches expected."""
        qc = QuantumCircuit(3)
        assert validate_qubit_count(qc, 3) is True

    def test_mismatch_qubit_count(self):
        """Test returning False when qubit count does not match expected."""
        qc = QuantumCircuit(2)
        assert validate_qubit_count(qc, 4) is False

    def test_zero_qubit_circuit(self):
        """Test qubit count check on empty 0-qubit circuit."""
        qc = QuantumCircuit(0)
        assert validate_qubit_count(qc, 0) is True
        assert validate_qubit_count(qc, 1) is False

    def test_non_circuit_input_raises_type_error(self):
        """Test passing a non-QuantumCircuit raises a TypeError."""
        with pytest.raises(TypeError, match="Expected a Qiskit QuantumCircuit"):
            validate_qubit_count("not_a_circuit", 2)  # type: ignore[arg-type]

    def test_invalid_expected_qubit_types_raise_type_error(self):
        """Test non-integer or boolean expected qubit counts raise TypeError."""
        qc = QuantumCircuit(2)
        with pytest.raises(TypeError, match="must be an integer"):
            validate_qubit_count(qc, 2.5)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="must be an integer"):
            validate_qubit_count(qc, True)  # type: ignore[arg-type]

    def test_negative_expected_qubit_raises_value_error(self):
        """Test negative expected qubit count raises ValueError."""
        qc = QuantumCircuit(2)
        with pytest.raises(ValueError, match="cannot be negative"):
            validate_qubit_count(qc, -1)


class TestHasMeasurements:
    """Test suite for has_measurements."""

    def test_circuit_without_measurements(self):
        """Test returning False for state preparation circuits without measure gates."""
        qc = phi_plus()
        assert has_measurements(qc) is False

    def test_circuit_with_measurements(self):
        """Test returning True when measurement gates are present."""
        qc = phi_plus()
        qc.measure_all()
        assert has_measurements(qc) is True

    def test_partial_measurement(self):
        """Test detecting measurement when only one qubit is measured."""
        qc = QuantumCircuit(2, 1)
        qc.h(0)
        qc.measure(0, 0)
        assert has_measurements(qc) is True

    def test_non_circuit_input_raises_type_error(self):
        """Test passing non-QuantumCircuit raises TypeError."""
        with pytest.raises(TypeError, match="Expected a Qiskit QuantumCircuit"):
            has_measurements(123)  # type: ignore[arg-type]


class TestValidateCircuit:
    """Test suite for validate_circuit master helper."""

    def test_validate_circuit_without_measurements_required(self):
        """Test validating qubit count without requiring measure gates."""
        qc = phi_plus()
        result = validate_circuit(qc, expected_qubits=2, require_measurements=False)
        assert result == {
            "qubit_count_valid": True,
            "has_measurements": False,
            "measurements_valid": True,
            "is_valid": True,
        }

    def test_validate_circuit_requiring_measurements_fail(self):
        """Test validation fails when measurements are required but absent."""
        qc = phi_plus()
        result = validate_circuit(qc, expected_qubits=2, require_measurements=True)
        assert result == {
            "qubit_count_valid": True,
            "has_measurements": False,
            "measurements_valid": False,
            "is_valid": False,
        }

    def test_validate_circuit_requiring_measurements_pass(self):
        """Test validation passes when measurements are required and present."""
        qc = phi_plus()
        qc.measure_all()
        result = validate_circuit(qc, expected_qubits=2, require_measurements=True)
        assert result == {
            "qubit_count_valid": True,
            "has_measurements": True,
            "measurements_valid": True,
            "is_valid": True,
        }

    def test_validate_circuit_qubit_mismatch(self):
        """Test validation fails when qubit count mismatches."""
        qc = QuantumCircuit(3)
        result = validate_circuit(qc, expected_qubits=2)
        assert result["qubit_count_valid"] is False
        assert result["is_valid"] is False

    def test_validate_circuit_invalid_type_raises(self):
        """Test invalid circuit argument raises TypeError."""
        with pytest.raises(TypeError, match="Expected a Qiskit QuantumCircuit"):
            validate_circuit(None)  # type: ignore[arg-type]
