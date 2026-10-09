"""Example: CHSH Bell Inequality Analysis in BellBox.

This script demonstrates:
1. Pure mathematical CHSH calculation from four specified correlation values.
2. Simulated quantum circuit CHSH experiment using optimal measurement settings for |Phi+>.
3. Scientific distinction between mathematical evaluation, simulation, and experiment.
"""

import math

import numpy as np

from bellbox import (
    calculate_chsh,
    calculate_correlations,
    phi_plus,
)


def run_mathematical_example() -> None:
    print("--------------------------------------------------")
    print(" 1. Mathematical CHSH Evaluation                  ")
    print("--------------------------------------------------")

    # Example theoretical correlations for optimal Bell state measurements: E = 1/sqrt(2) ~ 0.7071
    val = 1.0 / math.sqrt(2.0)
    e_ab = val
    e_ab_prime = val
    e_a_prime_b = val
    e_a_prime_b_prime = -val

    res = calculate_chsh(e_ab, e_ab_prime, e_a_prime_b, e_a_prime_b_prime)

    print(f"Correlations: E(a,b)={e_ab:.4f}, E(a,b')={e_ab_prime:.4f}, "
          f"E(a',b)={e_a_prime_b:.4f}, E(a',b')={e_a_prime_b_prime:.4f}")
    print(f"Calculated CHSH Parameter S: {res['s_value']:.4f}")
    print(f"Classical Bound |S| <= {res['classical_bound']}")
    print(f"Tsirelson Bound  |S| <= {res['tsirelson_bound']:.4f}")
    print(f"Violates Classical Bound?  {res['violates_classical_bound']}")
    print(f"Within Tsirelson Bound?    {res['within_tsirelson_bound']}\n")


def run_simulated_quantum_experiment() -> None:
    print("--------------------------------------------------")
    print(" 2. Simulated Quantum Experiment (|Phi+>)         ")
    print("--------------------------------------------------")
    print("Optimal CHSH Measurement Angles (X-Z plane):")
    print("  Alice: a = 0 rad (Z basis),  a' = pi/2 rad (X basis)")
    print("  Bob:   b = pi/4 rad (45 deg), b' = -pi/4 rad (-45 deg)\n")

    # Optimal measurement angles (in radians)
    settings = [
        ("e_ab", "a", "b", 0.0, np.pi / 4.0),
        ("e_ab_prime", "a", "b'", 0.0, -np.pi / 4.0),
        ("e_a_prime_b", "a'", "b", np.pi / 2.0, np.pi / 4.0),
        ("e_a_prime_b_prime", "a'", "b'", np.pi / 2.0, -np.pi / 4.0),
    ]

    computed_correlations: dict[str, float] = {}

    for key_name, name_a, name_b, theta_a, theta_b in settings:
        # Construct |Phi+> state circuit
        qc = phi_plus()

        # Apply basis rotation gates prior to computational Z-measurement:
        # To measure along angle theta in X-Z plane, apply Ry(-theta) before measurement.
        if theta_a != 0.0:
            qc.ry(-theta_a, 0)
        if theta_b != 0.0:
            qc.ry(-theta_b, 1)

        qc.measure_all()

        # Compute theoretical probability distribution for ideal simulation
        from qiskit.quantum_info import Statevector

        # Remove measure gates for statevector inspection
        qc_rot = qc.copy()
        qc_rot.remove_final_measurements(inplace=True)
        probs = Statevector(qc_rot).probabilities_dict()

        # Convert probabilities to shot counts (10,000 shots simulation)
        shot_counts = {k: int(v * 10000) for k, v in probs.items() if v > 0}
        corr_info = calculate_correlations(shot_counts)
        corr_val = corr_info["correlation"]

        computed_correlations[key_name] = corr_val

        print(f"Setting ({name_a}, {name_b}): theta_A={theta_a:.2f}, theta_B={theta_b:.2f} "
              f"-> Correlation E = {corr_val:+.4f}")

    # Pass four simulated correlations into calculate_chsh
    chsh_res = calculate_chsh(
        computed_correlations["e_ab"],
        computed_correlations["e_ab_prime"],
        computed_correlations["e_a_prime_b"],
        computed_correlations["e_a_prime_b_prime"],
    )

    print(f"\nSimulated CHSH Parameter S: {chsh_res['s_value']:.4f}")
    print(f"Violates Classical Bound (|S| > 2.0)? {chsh_res['violates_classical_bound']}\n")


def print_scientific_disclaimer() -> None:
    print("--------------------------------------------------")
    print(" Scientific Context & Disclaimers                 ")
    print("--------------------------------------------------")
    print("1. Pure Mathematical Analysis: Computes S = E(a,b) + E(a,b') + E(a',b) - E(a',b')")
    print("   from four given correlation values.")
    print("2. Simulated Quantum Experiment: Simulates noiseless circuit execution under ideal")
    print("   quantum mechanics. Demonstrates that quantum theory predicts S = 2*sqrt(2) > 2.")
    print("3. Physical Experimental Violation: Physical proof requires real hardware, detector")
    print("   efficiency calibration, loophole closures, and statistical error bars.")
    print("   Ideal simulator results prove theoretical model behavior, not physical hardware")
    print("   proof.")


def main() -> None:
    print("==================================================")
    print("     BellBox: CHSH Bell Inequality Analysis       ")
    print("==================================================\n")

    run_mathematical_example()
    run_simulated_quantum_experiment()
    print_scientific_disclaimer()

    print("\nDemonstration complete!")


if __name__ == "__main__":
    main()
