# BellBox — Quantum Circuit Experiments

**BellBox** is an educational and developer-oriented Python toolkit for constructing small quantum circuits, inspecting quantum states, converting measurement results into normalized probability distributions, and validating circuit structures.

BellBox relies on [Qiskit](https://github.com/Qiskit/qiskit) as its quantum simulation and state backend.

---

## Scope & Purpose

### What BellBox Does
- **Bell State Construction**: Helpers to build all four 2-qubit Bell states (`|\Phi^+>`, `|\Phi^->`, `|\Psi^+>`, `|\Psi^->`).
- **Measurement-Basis Support**: Prepares circuits for measurement in non-computational bases (`measure_in_basis`), applying unitary basis rotations for Pauli X, Y, and Z bases.
- **Measurement Analysis**: Analyzes raw shot measurement counts (`analyze_counts`) to calculate total shots and normalized probability distributions with strict input validation.
- **Two-Qubit Correlation Analysis**: Computes computational-basis correlation statistics (`calculate_correlations`) including outcome agreement/difference probabilities and normalized correlation coefficient $E = P(00) + P(11) - P(01) - P(10)$.
- **CHSH Bell Inequality Analysis**: Computes the CHSH statistic $S = E(a,b) + E(a,b') + E(a',b) - E(a',b')$ via `calculate_chsh` and evaluates violations against classical ($|S| \le 2$) and Tsirelson ($|S| \le 2\sqrt{2}$) bounds.
- **Distribution Validation**: Validates whether a probability distribution is properly normalized within numerical tolerances.
- **Circuit Inspection**: Provides basic structural validation helpers to check qubit counts and the presence of measurement gates.

### What BellBox Does NOT Do
- Does **not** implement a quantum simulator from scratch (leverages Qiskit's `Statevector` and circuit capabilities).
- Does **not** perform mathematical proof of circuit correctness or quantum entanglement (correlation in a single measurement basis measures basis dependence, not entanglement).
- Does **not** execute circuits on live physical quantum hardware backends.

---

## Installation

### Requirements
- Python 3.10 or higher
- Qiskit 1.0.0+

### Installation from Source

1. Clone or navigate to the repository directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   ```
   - On Windows (PowerShell):
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - On Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
3. Install BellBox in editable mode:
   ```bash
   pip install -e .
   ```
4. (Optional) Install development dependencies (pytest, ruff):
   ```bash
   pip install -e ".[dev]"
   ```

---

## Quick Start Examples

### 1. Constructing and Inspecting Bell States

```python
from qiskit.quantum_info import Statevector
from bellbox import phi_plus, psi_minus

# Construct |\Phi^+> = 1/sqrt(2) (|00> + |11>)
qc_phi = phi_plus()
sv_phi = Statevector(qc_phi)
print("|\Phi^+> Statevector:", sv_phi.data)
print("Theoretical probabilities:", sv_phi.probabilities_dict())

# Construct |\Psi^-> = 1/sqrt(2) (|10> - |01>)
qc_psi = psi_minus()
sv_psi = Statevector(qc_psi)
print("|\Psi^-> Statevector:", sv_psi.data)
```

### 2. Measurement Count Analysis and Validation

```python
from bellbox import analyze_counts, is_normalized

# Analyze raw measurement shot counts
counts = {"00": 512, "11": 488}
analysis = analyze_counts(counts)

print("Total shots:", analysis["total_shots"])
# Output: Total shots: 1000

print("Normalized probabilities:", analysis["probabilities"])
# Output: Normalized probabilities: {'00': 0.512, '11': 0.488}

# Validate distribution normalization
print("Is normalized?", is_normalized(analysis["probabilities"]))
# Output: True
```


### 3. Two-Qubit Correlation Analysis

```python
from bellbox import calculate_correlations

# Compute correlation coefficient and outcome statistics
counts = {"00": 512, "11": 488}
corrs = calculate_correlations(counts)

print("Correlation E:", corrs["correlation"])
# Output: Correlation E: 1.0

print("Agree probability:", corrs["agree_probability"])
# Output: Agree probability: 1.0
```


### 4. Measurement in Non-Computational Bases (X, Y, Z)

```python
from bellbox import phi_plus, measure_in_basis

qc = phi_plus()

# Prepare circuit for X-basis measurement (returns a new circuit by default)
qc_x = measure_in_basis(qc, "X")
print("X-basis circuit gates:", [inst.operation.name for inst in qc_x.data])
# Output includes 'h' rotation gates followed by 'measure'

# Measure qubit 0 in Y basis and qubit 1 in Z basis
qc_yz = measure_in_basis(qc, "YZ")
```


### 5. CHSH Bell Inequality Analysis

```python
import math
from bellbox import calculate_chsh

# Evaluate CHSH parameter S from 4 correlation values (e.g. 1/sqrt(2) ~ 0.7071)
val = 1.0 / math.sqrt(2.0)
chsh = calculate_chsh(val, val, val, -val)

print("S value:", chsh["s_value"])
# Output: S value: 2.8284271247461903 (Tsirelson bound 2*sqrt(2))

print("Violates classical bound (|S| > 2.0)?", chsh["violates_classical_bound"])
# Output: True
```


### 6. Circuit Validation

```python
from bellbox import phi_plus, validate_circuit

qc = phi_plus()
res = validate_circuit(qc, expected_qubits=2)
print("Validation result:", res)
# Output: {'qubit_count_valid': True, 'has_measurements': False, 'measurements_valid': True, 'is_valid': True}
```

---

## Running Examples, Tests, and Lint Checks

### Run Example Scripts
```bash
python examples/bell_states.py
python examples/chsh_inequality.py
```

### Run the Test Suite
```bash
pytest
```

### Run Linting Checks
```bash
ruff check .
```

---

## Current Limitations & Planned Improvements

- **Current Limitations**:
  - State preparation is currently limited to 2-qubit Bell states.
  - Verification helpers focus on structural checks (qubit count, measurement presence) rather than formal circuit equivalence verification.
- **Planned Improvements**:
  - Add multi-qubit state helpers (e.g., GHZ states, W states).
  - Add circuit visualization helpers.
  - Expand measurement analytics to compute quantum fidelity and state overlap metrics.

---

## Local Contribution

Refer to [CONTRIBUTING.md](CONTRIBUTING.md) for local setup, coding standards, and testing guidelines.

---

## License

This project is licensed under the [MIT License](LICENSE).
