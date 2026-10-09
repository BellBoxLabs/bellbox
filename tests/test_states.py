"""Tests for Bell state preparation functions and quantum state properties."""

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from bellbox.states import phi_minus, phi_plus, psi_minus, psi_plus


@pytest.mark.parametrize(
    "state_fn, expected_name",
    [
        (phi_plus, "phi_plus"),
        (phi_minus, "phi_minus"),
        (psi_plus, "psi_plus"),
        (psi_minus, "psi_minus"),
    ],
)
def test_bell_state_circuit_properties(state_fn, expected_name):
    """Test that Bell state functions return valid 2-qubit QuantumCircuit objects."""
    qc = state_fn()
    assert isinstance(qc, QuantumCircuit)
    assert qc.num_qubits == 2
    assert qc.num_clbits == 0
    assert qc.name == expected_name


def test_phi_plus_statevector():
    r"""Test |\Phi^+> = 1/sqrt(2) (|00> + |11>) statevector and global phase."""
    qc = phi_plus()
    sv = Statevector(qc)
    expected_data = np.array([1 / np.sqrt(2), 0, 0, 1 / np.sqrt(2)], dtype=complex)
    expected_sv = Statevector(expected_data)

    assert sv.equiv(expected_sv)

    # Test global phase rotation e^(i * pi / 3)
    phase_rotated_sv = Statevector(expected_data * np.exp(1j * np.pi / 3))
    assert sv.equiv(phase_rotated_sv)


def test_phi_minus_statevector():
    r"""Test |\Phi^-> = 1/sqrt(2) (|00> - |11>) statevector amplitudes."""
    qc = phi_minus()
    sv = Statevector(qc)
    expected_data = np.array([1 / np.sqrt(2), 0, 0, -1 / np.sqrt(2)], dtype=complex)
    expected_sv = Statevector(expected_data)

    assert sv.equiv(expected_sv)


def test_psi_plus_statevector():
    r"""Test |\Psi^+> = 1/sqrt(2) (|01> + |10>) statevector amplitudes."""
    qc = psi_plus()
    sv = Statevector(qc)
    expected_data = np.array([0, 1 / np.sqrt(2), 1 / np.sqrt(2), 0], dtype=complex)
    expected_sv = Statevector(expected_data)

    assert sv.equiv(expected_sv)


def test_psi_minus_statevector():
    r"""Test |\Psi^-> = 1/sqrt(2) (|10> - |01>) statevector amplitudes."""
    qc = psi_minus()
    sv = Statevector(qc)
    expected_data = np.array([0, -1 / np.sqrt(2), 1 / np.sqrt(2), 0], dtype=complex)
    expected_sv = Statevector(expected_data)

    assert sv.equiv(expected_sv)


@pytest.mark.parametrize(
    "state_fn, expected_probs",
    [
        (phi_plus, {"00": 0.5, "11": 0.5, "01": 0.0, "10": 0.0}),
        (phi_minus, {"00": 0.5, "11": 0.5, "01": 0.0, "10": 0.0}),
        (psi_plus, {"01": 0.5, "10": 0.5, "00": 0.0, "11": 0.0}),
        (psi_minus, {"01": 0.5, "10": 0.5, "00": 0.0, "11": 0.0}),
    ],
)
def test_bell_state_measurement_correlations(state_fn, expected_probs):
    """Test exact theoretical measurement probabilities for all Bell states."""
    qc = state_fn()
    sv = Statevector(qc)
    probs = sv.probabilities_dict()

    for bitstring, expected_prob in expected_probs.items():
        assert pytest.approx(probs.get(bitstring, 0.0), abs=1e-6) == expected_prob
