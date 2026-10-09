"""Quantum state preparation functions for fundamental entangled states.

This module provides functions to construct the four Maximally Entangled 2-qubit
Bell states (also known as EPR pairs) using Qiskit.
"""

from qiskit import QuantumCircuit


def phi_plus() -> QuantumCircuit:
    r"""Construct the Bell state |\Phi^+> = 1/\sqrt{2} (|00> + |11>).

    The circuit applies a Hadamard gate to qubit 0 followed by a CNOT (CX) gate
    controlled on qubit 0 with target on qubit 1.

    Returns:
        QuantumCircuit: A 2-qubit circuit preparing |\Phi^+>.
    """
    qc = QuantumCircuit(2, name="phi_plus")
    qc.h(0)
    qc.cx(0, 1)
    return qc


def phi_minus() -> QuantumCircuit:
    """Construct |Phi-> = (|00> - |11>) / sqrt(2)."""
    qc = QuantumCircuit(2, name="phi_minus")
    qc.h(0)
    qc.z(0)
    qc.cx(0, 1)
    return qc


def psi_plus() -> QuantumCircuit:
    """Construct |Psi+> = (|01> + |10>) / sqrt(2)."""
    qc = QuantumCircuit(2, name="psi_plus")
    qc.h(0)
    qc.cx(0, 1)
    qc.x(1)
    return qc


def psi_minus() -> QuantumCircuit:
    r"""Construct the Bell state |\Psi^-> = 1/\sqrt{2} (|10> - |01>).

    The circuit applies Pauli-X on qubit 0 and qubit 1, followed by Hadamard on qubit 0,
    and a CNOT gate controlled on qubit 0 with target on qubit 1.

    Note that |\Psi^-> is equivalent up to a global phase of -1 to
    1/\sqrt{2} (|01> - |10>).

    Returns:
        QuantumCircuit: A 2-qubit circuit preparing |\Psi^->.
    """
    qc = QuantumCircuit(2, name="psi_minus")
    qc.x(0)
    qc.x(1)
    qc.h(0)
    qc.cx(0, 1)
    return qc
