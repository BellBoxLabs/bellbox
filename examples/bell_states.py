"""Example: Constructing and Analyzing Bell States with BellBox.

This script demonstrates:
1. Constructing all four 2-qubit Bell states (|Phi+>, |Phi->, |Psi+>, |Psi->).
2. Inspecting quantum statevectors and theoretical measurement distributions.
3. Simulating measurement shot counts and converting them to normalized probabilities.
4. Validating circuit structure and probability distribution normalization.
"""

from qiskit.quantum_info import Statevector

from bellbox import (
    analyze_counts,
    calculate_correlations,
    is_normalized,
    measure_in_basis,
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
    print(" Analyzing Measurement Counts & Probabilities    ")
    print("--------------------------------------------------")

    # Example shot counts from a measurement experiment
    simulated_counts = {"00": 512, "11": 488}
    print(f"Raw measurement counts: {simulated_counts}")

    analysis = analyze_counts(simulated_counts)
    print(f"Total shots analyzed: {analysis['total_shots']}")
    print(f"Normalized probabilities: {analysis['probabilities']}")

    normalized_check = is_normalized(analysis["probabilities"])
    print(f"Is distribution normalized? {normalized_check}")

    correlations = calculate_correlations(simulated_counts)
    print(f"Outcome agreement count: {correlations['agree_count']}")
    print(f"Outcome agreement prob:  {correlations['agree_probability']:.3f}")
    print(f"Correlation coefficient: {correlations['correlation']:.3f}\n")

    print("--------------------------------------------------")
    print(" Multi-Basis Measurement Behavior for |Phi+>       ")
    print("--------------------------------------------------")

    qc_base = phi_plus()
    for basis in ("Z", "X", "Y"):
        # Prepare measurement circuit in specified basis (returns a copy)
        qc_meas = measure_in_basis(qc_base, basis, inplace=False)

        # Inspect rotation gates added prior to measurement
        gate_names = [inst.operation.name for inst in qc_meas.data]

        # Evaluate theoretical probability distribution right before Z-measurement
        # (Exclude final measure operations for Statevector inspection)
        qc_rotation_only = qc_meas.copy()
        qc_rotation_only.remove_final_measurements(inplace=True)
        sv = Statevector(qc_rotation_only)
        theory_probs = {k: round(v, 4) for k, v in sv.probabilities_dict().items()}

        # Compute theoretical correlation
        # Convert probabilities dict to simulated shot counts for correlation helper
        theory_counts = {k: int(v * 1000) for k, v in theory_probs.items() if v > 0}
        corr_res = calculate_correlations(theory_counts)

        print(f"Basis: {basis} | Gates: {gate_names}")
        print(f"  Theoretical Probabilities: {theory_probs}")
        print(f"  Correlation Coefficient E: {corr_res['correlation']:+.2f}")
        print()

    print("Note: Computational-basis correlation alone (E = +1) does not establish quantum")
    print("entanglement. Observing how correlations vary systematically across multiple")
    print("complementary measurement bases (e.g., Z, X, Y) highlights quantum state behavior.")

    print("\nDemonstration complete!")


if __name__ == "__main__":
    main()
