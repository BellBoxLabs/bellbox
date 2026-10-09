# BellBox — Quantum Circuit Experiments

**BellBox** is an educational and developer-oriented Python toolkit for constructing small quantum circuits, inspecting quantum states, converting measurement results into normalized probability distributions, and validating circuit structures.

BellBox relies on [Qiskit](https://github.com/Qiskit/qiskit) as its quantum simulation and state backend.

---

## Scope & Purpose

### What BellBox Does
- **Bell State Construction**: Helpers to build all four 2-qubit Bell states (`|\Phi^+>`, `|\Phi^->`, `|\Psi^+>`, `|\Psi^->`).
- **Measurement Analysis**: Analyzes raw shot measurement counts (`analyze_counts`) to calculate total shots and normalized probability distributions with strict input validation.
- **Distribution Validation**: Validates whether a probability distribution is properly normalized within numerical tolerances.
- **Circuit Inspection**: Provides basic structural validation helpers to check qubit counts and the presence of measurement gates.

### What BellBox Does NOT Do
- Does **not** implement a quantum simulator from scratch (leverages Qiskit's `Statevector` and circuit capabilities).
- Does **not** perform mathematical proof of circuit correctness (structural checks verify surface properties like qubit count, not algorithm correctness).
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


### 3. Circuit Validation

```python
from bellbox import phi_plus, validate_circuit

qc = phi_plus()
res = validate_circuit(qc, expected_qubits=2)
print("Validation result:", res)
# Output: {'qubit_count_valid': True, 'has_measurements': False, 'measurements_valid': True, 'is_valid': True}
```

---

## Running Examples, Tests, and Lint Checks

### Run the Bell State Example Script
```bash
python examples/bell_states.py
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
