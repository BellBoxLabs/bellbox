"""Circuit validation helpers for Qiskit QuantumCircuit instances.

This module provides simple, lightweight helpers to inspect structural properties of
quantum circuits, such as qubit count and presence of measurement operations.

IMPORTANT DISCLAIMER:
    Structural validation verifies basic circuit parameters (e.g. qubit count,
    presence of measure gates). Structural validity DOES NOT prove or guarantee
    that a quantum circuit is mathematically correct, unitary, non-trivial, or
    produces a specific target state.
"""

from typing import Any

from qiskit import QuantumCircuit


def validate_qubit_count(circuit: QuantumCircuit, expected_qubits: int) -> bool:
    """Check whether a QuantumCircuit has the expected number of qubits.

    Args:
        circuit: The Qiskit QuantumCircuit to validate.
        expected_qubits: The expected non-negative integer qubit count.

    Returns:
        bool: True if circuit.num_qubits == expected_qubits, False otherwise.

    Raises:
        TypeError: If `circuit` is not a QuantumCircuit or `expected_qubits` is not an integer.
        ValueError: If `expected_qubits` is negative.
    """
    if not isinstance(circuit, QuantumCircuit):
        raise TypeError(f"Expected a Qiskit QuantumCircuit, got {type(circuit).__name__}.")

    if isinstance(expected_qubits, bool) or not isinstance(expected_qubits, int):
        raise TypeError(
            f"Expected qubit count must be an integer, got {type(expected_qubits).__name__}."
        )

    if expected_qubits < 0:
        raise ValueError(f"Expected qubit count cannot be negative, got {expected_qubits}.")

    return circuit.num_qubits == expected_qubits


def has_measurements(circuit: QuantumCircuit) -> bool:
    """Check whether a QuantumCircuit contains any measurement operations.

    Args:
        circuit: The Qiskit QuantumCircuit to inspect.

    Returns:
        bool: True if the circuit contains at least one measurement gate, False otherwise.

    Raises:
        TypeError: If `circuit` is not a QuantumCircuit.
    """
    if not isinstance(circuit, QuantumCircuit):
        raise TypeError(f"Expected a Qiskit QuantumCircuit, got {type(circuit).__name__}.")

    return any(instruction.operation.name == "measure" for instruction in circuit.data)


def validate_circuit(
    circuit: QuantumCircuit,
    expected_qubits: int | None = None,
    require_measurements: bool = False,
) -> dict[str, Any]:
    """Perform basic structural validation checks on a QuantumCircuit.

    Args:
        circuit: The Qiskit QuantumCircuit to validate.
        expected_qubits: Optional expected qubit count. If None, qubit count check passes.
        require_measurements: If True, requires the circuit to contain measurement operations.

    Returns:
        dict[str, Any]: A dictionary summarizing check results:
            - 'qubit_count_valid' (bool)
            - 'has_measurements' (bool)
            - 'measurements_valid' (bool)
            - 'is_valid' (bool)

    Raises:
        TypeError: If input types are invalid.
        ValueError: If expected_qubits is negative.

    Note:
        Structural validation checks only surface properties (qubit count, measurement gates).
        It does NOT guarantee mathematical or algorithmic correctness of the quantum logic.
    """
    if not isinstance(circuit, QuantumCircuit):
        raise TypeError(f"Expected a Qiskit QuantumCircuit, got {type(circuit).__name__}.")

    if expected_qubits is not None:
        qubit_count_ok = validate_qubit_count(circuit, expected_qubits)
    else:
        qubit_count_ok = True

    meas_present = has_measurements(circuit)
    meas_ok = (not require_measurements) or meas_present

    return {
        "qubit_count_valid": qubit_count_ok,
        "has_measurements": meas_present,
        "measurements_valid": meas_ok,
        "is_valid": qubit_count_ok and meas_ok,
    }
