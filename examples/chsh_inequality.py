"""Example: CHSH Bell Inequality Analysis in BellBox.

This script demonstrates:
1. Pure mathematical CHSH calculation from four specified correlation values.
2. Simulated quantum circuit CHSH experiment using optimal measurement settings for |Phi+>.
3. Scientific distinction between mathematical evaluation, simulation, and experiment.
"""

import math

import numpy as np

from bellbox import (
    TSIRELSON_CHSH_BOUND,
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
    print(" 2. Quantum Circuit Experiment for |Phi+>         ")
    print("--------------------------------------------------")
    print("Measurement Convention:  E = P(00) + P(11) - P(01) - P(10)")
    print("CHSH Sign Convention:    S = E(a,b) + E(a,b') + E(a',b) - E(a',b')\n")
    print("Optimal Measurement Angles (X-Z plane):")
    print("  Alice (qubit 0): a  = 0 rad (0 deg),   a' = pi/2 rad (90 deg)")
    print("  Bob   (qubit 1): b  = pi/4 rad (45 deg), b' = -pi/4 rad (-45 deg)\n")

    # Optimal measurement setting pairs
    settings = [
        ("e_ab", "a", "b", 0.0, np.pi / 4.0),
        ("e_ab_prime", "a", "b'", 0.0, -np.pi / 4.0),
        ("e_a_prime_b", "a'", "b", np.pi / 2.0, np.pi / 4.0),
        ("e_a_prime_b_prime", "a'", "b'", np.pi / 2.0, -np.pi / 4.0),
    ]

    exact_correlations: dict[str, float] = {}
    sampled_correlations: dict[str, float] = {}

    from qiskit.quantum_info import Statevector

    for key_name, name_a, name_b, theta_a, theta_b in settings:
        # 1. Construct |Phi+> state circuit
        qc = phi_plus()

        # Apply measurement basis rotation gates in X-Z plane:
        # Rotating measurement basis by theta requires applying Ry(-theta) prior to Z-measurement.
        if theta_a != 0.0:
            qc.ry(-theta_a, 0)
        if theta_b != 0.0:
            qc.ry(-theta_b, 1)

        # 2. Exact Quantum Probabilities via Statevector (no shot truncation)
        probs = Statevector(qc).probabilities_dict()
        p00 = probs.get("00", 0.0)
        p11 = probs.get("11", 0.0)
        p01 = probs.get("01", 0.0)
        p10 = probs.get("10", 0.0)
        e_exact = (p00 + p11) - (p01 + p10)
        exact_correlations[key_name] = e_exact

        # 3. Finite-Shot Sampling Simulation (10,000 shots)
        shot_counts = {k: int(round(v * 10000)) for k, v in probs.items() if v > 0}
        corr_sampled_info = calculate_correlations(shot_counts)
        e_sampled = corr_sampled_info["correlation"]
        sampled_correlations[key_name] = e_sampled

        print(f"Setting ({name_a}, {name_b}): theta_A={theta_a:.2f}, theta_B={theta_b:+.2f}")
        print(f"  Exact Probabilities: P(00)={p00:.4f}, P(11)={p11:.4f}, "
              f"P(01)={p01:.4f}, P(10)={p10:.4f}")
        print(f"  Exact E = {e_exact:+.6f} | Sampled (10k shots) E = {e_sampled:+.6f}\n")

    # Evaluate CHSH S parameters
    exact_chsh = calculate_chsh(
        exact_correlations["e_ab"],
        exact_correlations["e_ab_prime"],
        exact_correlations["e_a_prime_b"],
        exact_correlations["e_a_prime_b_prime"],
    )

    sampled_chsh = calculate_chsh(
        sampled_correlations["e_ab"],
        sampled_correlations["e_ab_prime"],
        sampled_correlations["e_a_prime_b"],
        sampled_correlations["e_a_prime_b_prime"],
    )

    print("--------------------------------------------------")
    print(" Summary of CHSH Results                          ")
    print("--------------------------------------------------")
    print(f"Exact Quantum CHSH Parameter S: {exact_chsh['s_value']:.12f}")
    print(f"  Tsirelson Bound (2*sqrt(2)):   {TSIRELSON_CHSH_BOUND:.12f}")
    is_exact_match = abs(exact_chsh['s_value'] - TSIRELSON_CHSH_BOUND) < 1e-12
    print(f"  Exact Match?                   {is_exact_match}")
    print(f"Sampled Quantum CHSH Parameter S:{sampled_chsh['s_value']:.6f}")
    print(f"  Violates Classical Bound (|S|>2)? {exact_chsh['violates_classical_bound']}\n")


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
