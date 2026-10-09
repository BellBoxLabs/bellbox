"""Utilities for analyzing quantum measurement results and probability distributions.

This module provides tools to convert raw measurement counts (shot counts) into
normalized probability distributions and to validate distribution properties.
"""

import math
from collections.abc import Mapping, Sequence
from typing import Any

from qiskit import QuantumCircuit

from bellbox.validation import has_measurements


def analyze_counts(counts: Mapping[str, int]) -> dict[str, Any]:
    """Analyze quantum measurement counts and compute statistics.

    Args:
        counts: A dictionary-like mapping of bitstrings (e.g. '00', '01')
            to non-negative integer shot counts.

    Returns:
        dict[str, Any]: A dictionary containing analysis statistics:
            - 'total_shots' (int): Total number of measurement shots across all outcomes.
            - 'probabilities' (dict[str, float]): Dictionary mapping bitstrings to estimated
              probabilities, sorted lexicographically by bitstring.

    Raises:
        TypeError: If `counts` is not a Mapping, if any key is not a string,
            or if any count is not an integer (or is a boolean).
        ValueError: If any bitstring contains characters other than '0' or '1',
            if bitstring lengths are inconsistent, if any count is negative,
            or if total counts sum to zero for a non-empty mapping.
    """
    if not isinstance(counts, Mapping):
        raise TypeError(f"Counts must be a dictionary-like mapping, got {type(counts).__name__}.")

    if not counts:
        return {"total_shots": 0, "probabilities": {}}

    total_shots = 0
    validated_counts: list[tuple[str, int]] = []
    expected_length: int | None = None

    for bitstring, count in counts.items():
        if not isinstance(bitstring, str):
            raise TypeError(
                f"Bitstring key must be a string, got {type(bitstring).__name__}: {bitstring!r}."
            )

        if not bitstring or any(char not in ("0", "1") for char in bitstring):
            raise ValueError(f"Invalid bitstring key {bitstring!r}: must contain only '0' and '1'.")

        if expected_length is None:
            expected_length = len(bitstring)
        elif len(bitstring) != expected_length:
            raise ValueError(
                f"Inconsistent bitstring length: expected {expected_length}, "
                f"got {len(bitstring)} for key {bitstring!r}."
            )

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

    probabilities = {bitstring: count / total_shots for bitstring, count in validated_counts}

    return {
        "total_shots": total_shots,
        "probabilities": probabilities,
    }


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
            if bitstring lengths are inconsistent, if any count is negative,
            or if total counts sum to zero.

    Bitstring and Output Ordering:
        Bitstrings in Qiskit follow little-endian ordering by convention
        (qubit n-1 ... qubit 0). The returned dictionary keys are sorted
        lexicographically to ensure deterministic iteration order regardless of input dict order.
    """
    analysis = analyze_counts(counts)
    return analysis["probabilities"]



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


def calculate_correlations(counts: Mapping[str, int]) -> dict[str, Any]:
    """Calculate two-qubit measurement correlation statistics from shot counts.

    For two-qubit computational basis measurements, outcomes are bitstrings of length 2
    ('00', '01', '10', '11'). Bit values 0 and 1 map to eigenvalue observables +1 and -1.
    The computational-basis correlation coefficient is defined as:

        E = P(00) + P(11) - P(01) - P(10) = P(agree) - P(differ)

    Args:
        counts: A dictionary-like mapping of 2-bit strings to non-negative integer shot counts.

    Returns:
        dict[str, Any]: A dictionary containing correlation analysis results:
            - 'total_shots' (int): Total number of measurement shots across all outcomes.
            - 'agree_count' (int): Total count of agreeing outcomes ('00' and '11').
            - 'agree_probability' (float): Estimated probability of agreeing outcomes,
              P(00) + P(11).
            - 'differ_count' (int): Total count of differing outcomes ('01' and '10').
            - 'differ_probability' (float): Estimated probability of differing outcomes,
              P(01) + P(10).
            - 'correlation' (float): The normalized correlation coefficient E in [-1.0, 1.0].

    Raises:
        TypeError: If `counts` is not a Mapping, if any key is not a string,
            or if any count value is not an integer (or is a boolean).
        ValueError: If any key is not a 2-bit binary string (only '0' and '1', length 2),
            if any count is negative, or if total counts sum to zero for a non-empty mapping.

    Note:
        A correlation coefficient of +1 or -1 in a single measurement basis (such as the
        computational Z-basis) measures statistical dependence in that basis, but does NOT by
        itself prove quantum entanglement. Demonstrating quantum entanglement requires
        measuring correlations across multiple non-commuting bases (e.g., CHSH violation).
    """
    if not isinstance(counts, Mapping):
        raise TypeError(f"Counts must be a dictionary-like mapping, got {type(counts).__name__}.")

    if not counts:
        return {
            "total_shots": 0,
            "agree_count": 0,
            "agree_probability": 0.0,
            "differ_count": 0,
            "differ_probability": 0.0,
            "correlation": 0.0,
        }

    total_shots = 0
    outcome_counts: dict[str, int] = {"00": 0, "01": 0, "10": 0, "11": 0}

    for bitstring, count in counts.items():
        if not isinstance(bitstring, str):
            raise TypeError(
                f"Bitstring key must be a string, got {type(bitstring).__name__}: {bitstring!r}."
            )

        if any(char not in ("0", "1") for char in bitstring):
            raise ValueError(f"Invalid bitstring key {bitstring!r}: must contain only '0' and '1'.")

        if len(bitstring) != 2:
            raise ValueError(
                f"Bitstring key {bitstring!r} must have length 2 for two-qubit correlation "
                f"analysis, got length {len(bitstring)}."
            )

        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError(
                f"Count for bitstring {bitstring!r} must be an integer, got {type(count).__name__}."
            )

        if count < 0:
            raise ValueError(f"Count for bitstring {bitstring!r} cannot be negative, got {count}.")

        total_shots += count
        outcome_counts[bitstring] += count

    if total_shots == 0:
        raise ValueError("Total measurement count is zero; cannot calculate correlations.")

    agree_count = outcome_counts["00"] + outcome_counts["11"]
    differ_count = outcome_counts["01"] + outcome_counts["10"]

    agree_probability = agree_count / total_shots
    differ_probability = differ_count / total_shots
    correlation = agree_probability - differ_probability

    return {
        "total_shots": total_shots,
        "agree_count": agree_count,
        "agree_probability": agree_probability,
        "differ_count": differ_count,
        "differ_probability": differ_probability,
        "correlation": correlation,
    }


def measure_in_basis(
    circuit: QuantumCircuit,
    basis: str | Sequence[str] = "Z",
    inplace: bool = False,
) -> QuantumCircuit:
    """Prepare a quantum circuit for measurement in specified Pauli bases (X, Y, or Z).

    Quantum hardware and standard simulators perform measurements exclusively in the computational
    (Pauli-Z) basis. To measure in non-computational bases, unitary basis-change operations are
    applied immediately before Z-basis measurement:
    - **Z basis**: No transformation needed (computational basis).
    - **X basis**: Apply Hadamard (H) gate: maps X-eigenstates |+>, |-> to Z-eigenstates |0>, |1>.
    - **Y basis**: Apply S-dagger (SDG) gate then Hadamard (H) gate: maps Y-eigenstates |+i>, |-i>
      to Z-eigenstates |0>, |1>.

    Args:
        circuit: The Qiskit QuantumCircuit to prepare for measurement.
        basis: A string ('X', 'Y', 'Z') applied to all qubits, a string specifying per-qubit bases
            (e.g. 'XZ'), or a sequence of basis strings (e.g. ['X', 'Z']). Default is 'Z'.
        inplace: If True, modifies and returns the input circuit. If False (default), returns a
            copy of the circuit with measurement operations added.

    Returns:
        QuantumCircuit: The circuit updated with basis-change gates and measurement operations.

    Raises:
        TypeError: If `circuit` is not a QuantumCircuit, `basis` is of invalid type, or `inplace`
            is not a boolean.
        ValueError: If `circuit` has 0 qubits, already contains measurement operations, if basis
            sequence length does not match qubit count, or if an unrecognized basis name is given.

    Note:
        Applying basis-change gates does not permanently alter the physical quantum state prior to
        measurement; it rotates the measurement reference axes so that standard Z-basis measurement
        projects the state onto the desired Pauli eigenbasis.
    """
    if not isinstance(circuit, QuantumCircuit):
        raise TypeError(f"Expected a Qiskit QuantumCircuit, got {type(circuit).__name__}.")

    if not isinstance(inplace, bool):
        raise TypeError(f"Expected bool for inplace parameter, got {type(inplace).__name__}.")

    if circuit.num_qubits == 0:
        raise ValueError("Cannot apply measurement to a circuit with 0 qubits.")

    if has_measurements(circuit):
        raise ValueError(
            "Circuit already contains measurement operations. Basis measurements must be added "
            "before any measurement operations."
        )

    bases: tuple[str, ...]
    if isinstance(basis, str):
        raw_basis = basis.strip().upper()
        if len(raw_basis) == 1:
            bases = (raw_basis,) * circuit.num_qubits
        elif len(raw_basis) == circuit.num_qubits:
            bases = tuple(raw_basis)
        else:
            raise ValueError(
                f"Invalid basis string length {len(raw_basis)} for a {circuit.num_qubits}-qubit "
                f"circuit. Must be 1 character or match qubit count ({circuit.num_qubits})."
            )
    elif isinstance(basis, Sequence) and not isinstance(basis, (str, bytes)):
        if len(basis) != circuit.num_qubits:
            raise ValueError(
                f"Basis sequence length {len(basis)} does not match qubit count "
                f"({circuit.num_qubits})."
            )
        normalized_bases: list[str] = []
        for elem in basis:
            if not isinstance(elem, str):
                raise TypeError(
                    f"Basis element must be a string, got {type(elem).__name__}: {elem!r}."
                )
            elem_str = elem.strip().upper()
            if len(elem_str) != 1:
                raise ValueError(
                    f"Each basis element must be a single character, got {elem!r}."
                )
            normalized_bases.append(elem_str)
        bases = tuple(normalized_bases)
    else:
        raise TypeError(
            f"Basis must be a string or sequence of strings, got {type(basis).__name__}."
        )

    for b in bases:
        if b not in ("X", "Y", "Z"):
            raise ValueError(f"Invalid measurement basis {b!r}. Supported bases are 'X', 'Y', 'Z'.")

    target_qc = circuit if inplace else circuit.copy()

    for qubit_idx, b in enumerate(bases):
        if b == "X":
            target_qc.h(qubit_idx)
        elif b == "Y":
            target_qc.sdg(qubit_idx)
            target_qc.h(qubit_idx)
        elif b == "Z":
            pass

    if target_qc.num_clbits == 0:
        target_qc.measure_all()
    else:
        for qubit_idx in range(target_qc.num_qubits):
            target_qc.measure(qubit_idx, qubit_idx)

    return target_qc


