"""Example: Constructing and Analyzing Bell States with BellBox.

This script demonstrates:
1. Constructing all four 2-qubit Bell states (|Phi+>, |Phi->, |Psi+>, |Psi->).
2. Inspecting quantum statevectors and theoretical measurement distributions.
3. Simulating measurement shot counts and converting them to normalized probabilities.
4. Validating circuit structure and probability distribution normalization.
"""

from qiskit.quantum_info import Statevector

from bellbox import (
    counts_to_probabilities,
    is_normalized,
    phi_minus,
    phi_plus,
    psi_minus,
    psi_plus,
    validate_circuit,
)


def main() -> None:
    print("==================================================")
    print("        BellBox: Bell States Demonstration        ")
    print("==================================================\n")

    bell_state_creators = [
        ("|Phi+>", phi_plus),
        ("|Phi->", phi_minus),
        ("|Psi+>", psi_plus),
        ("|Psi->", psi_minus),
    ]

    for label, creator_fn in bell_state_creators:
        qc = creator_fn()
        sv = Statevector(qc)
        probs = sv.probabilities_dict()

        # Perform structural validation
        val_result = validate_circuit(qc, expected_qubits=2)

        print(f"--- {label} (Circuit: '{qc.name}') ---")
        print(f"Qubits: {qc.num_qubits}")
        print(f"Statevector: {sv.data}")
        print(f"Theoretical Probabilities: {probs}")
        print(f"Structural Validation Passed: {val_result['is_valid']}")
        print()

    print("--------------------------------------------------")
    print(" Converting Measurement Counts to Probabilities  ")
    print("--------------------------------------------------")

    # Example shot counts from a measurement experiment
    simulated_counts = {"00": 512, "11": 488}
    print(f"Raw measurement counts: {simulated_counts}")

    prob_dist = counts_to_probabilities(simulated_counts)
    print(f"Normalized probabilities: {prob_dist}")

    normalized_check = is_normalized(prob_dist)
    print(f"Is distribution normalized? {normalized_check}")

    print("\nDemonstration complete!")


if __name__ == "__main__":
    main()
