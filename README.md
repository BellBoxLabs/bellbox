# BellBox — Quantum Circuit & Correlation Analysis Toolkit

**BellBox** is an educational and developer-oriented Python toolkit built on [Qiskit](https://github.com/Qiskit/qiskit). It provides intuitive, robust utilities for preparing 2-qubit Bell states, configuring measurement bases, analyzing raw measurement shot counts, computing correlation coefficients, and evaluating CHSH Bell inequality violations.

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [Bell State Preparation](#bell-state-preparation)
  - [Measurement & Basis Support](#measurement--basis-support)
  - [Shot Count & Probability Analysis](#shot-count--probability-analysis)
  - [Two-Qubit Correlation Analysis](#two-qubit-correlation-analysis)
  - [CHSH Bell Inequality Analysis](#chsh-bell-inequality-analysis)
  - [Circuit Validation Helpers](#circuit-validation-helpers)
- [Example Scripts](#example-scripts)
- [Scientific Concepts & Conventions](#scientific-concepts--conventions)
- [Development and Testing](#development-and-testing)
- [Limitations](#limitations)

---

## Overview

### What BellBox Does
- **Bell State Preparation**: Constructs standard 2-qubit Maximally Entangled Bell states (`|\Phi^+>`, `|\Phi^->`, `|\Psi^+>`, `|\Psi^->`).
- **Basis-Aware Measurement**: Prepares quantum circuits for measurement in non-computational Pauli bases ($X$, $Y$, or $Z$) by appending unitary basis-change gates prior to measurement.
- **Shot Count & Probability Analysis**: Converts raw measurement outcome counts into normalized probability distributions with strict input validation.
- **Two-Qubit Correlation Analysis**: Computes computational-basis correlation coefficients ($E = P(00) + P(11) - P(01) - P(10)$) from shot count distributions.
- **CHSH Bell Inequality Analysis**: Computes the CHSH parameter $S = E(a,b) + E(a,b') + E(a',b) - E(a',b')$ and evaluates violations against classical ($|S| \le 2.0$) and Tsirelson ($|S| \le 2\sqrt{2}$) bounds.
- **Structural Circuit Inspection**: Checks circuit properties such as qubit count and presence of measurement gates.

### Relationship to Qiskit
BellBox relies directly on Qiskit (`qiskit.QuantumCircuit` and `qiskit.quantum_info.Statevector`) as its underlying quantum circuit representation and simulation backend.

---

## Installation

### Prerequisites
- **Python**: Version 3.10 or higher
- **Qiskit**: Version 1.0.0 or higher

### Installing from Source

1. Clone or download the repository and navigate into the project directory:
   ```bash
   cd bellbox  # Or enter your cloned project directory
   ```

2. Create and activate a Python virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt)**:
     ```cmd
     python -m venv .venv
     .\.venv\Scripts\activate.bat
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Install BellBox in editable mode:
   ```bash
   pip install -e .
   ```

4. *(Optional)* Install development dependencies (`pytest`, `ruff`):
   ```bash
   pip install -e ".[dev]"
   ```

---

## Quick Start

The following copyable example demonstrates creating a Bell state, preparing it for basis measurement, analyzing raw measurement shot counts, computing two-qubit correlation statistics, and evaluating the CHSH Bell inequality:

```python
import math
from qiskit.quantum_info import Statevector
from bellbox import (
    phi_plus,
    measure_in_basis,
    analyze_counts,
    calculate_correlations,
    calculate_chsh,
)

# 1. Prepare a 2-qubit Bell state |\Phi^+> = 1/sqrt(2) (|00> + |11>)
qc = phi_plus()
print("Circuit name:", qc.name)

# 2. Configure circuit for measurement in the X basis (returns a copy by default)
qc_x = measure_in_basis(qc, "X", inplace=False)
print("X-basis gates:", [inst.operation.name for inst in qc_x.data])

# 3. Analyze raw measurement shot counts (illustrative counts dictionary)
counts = {"00": 512, "11": 488}  # Note: Illustrative counts (not sampled directly from qc_x above)
analysis = analyze_counts(counts)
print("Total shots:", analysis["total_shots"])
print("Probabilities:", analysis["probabilities"])

# 4. Calculate correlation coefficient E = P(00) + P(11) - P(01) - P(10)
corr = calculate_correlations(counts)
print("Correlation E:", corr["correlation"])

# 5. Evaluate CHSH statistic S = E(a,b) + E(a,b') + E(a',b) - E(a',b')
val = 1.0 / math.sqrt(2.0)  # ~0.70710678
chsh = calculate_chsh(val, val, val, -val)
print("CHSH Parameter S:", chsh["s_value"])
print("Violates Classical Bound (|S| > 2.0)?", chsh["violates_classical_bound"])
```

---

## API Reference

All public functions and constants are exported at the top-level `bellbox` package.

### Bell State Preparation

Found in `bellbox.states`.

#### `phi_plus() -> QuantumCircuit`
Constructs the 2-qubit Bell state $|\Phi^+\rangle = \frac{1}{\sqrt{2}} (|00\rangle + |11\rangle)$.
- **Returns**: `QuantumCircuit` named `"phi_plus"` with 2 qubits.

#### `phi_minus() -> QuantumCircuit`
Constructs the 2-qubit Bell state $|\Phi^-\rangle = \frac{1}{\sqrt{2}} (|00\rangle - |11\rangle)$.
- **Returns**: `QuantumCircuit` named `"phi_minus"` with 2 qubits.

#### `psi_plus() -> QuantumCircuit`
Constructs the 2-qubit Bell state $|\Psi^+\rangle = \frac{1}{\sqrt{2}} (|01\rangle + |10\rangle)$.
- **Returns**: `QuantumCircuit` named `"psi_plus"` with 2 qubits.

#### `psi_minus() -> QuantumCircuit`
Constructs the 2-qubit Bell state $|\Psi^-\rangle = \frac{1}{\sqrt{2}} (|10\rangle - |01\rangle)$.
- **Returns**: `QuantumCircuit` named `"psi_minus"` with 2 qubits.

---

### Measurement & Basis Support

Found in `bellbox.measurement`.

#### `measure_in_basis(circuit: QuantumCircuit, basis: str | Sequence[str] = "Z", inplace: bool = False) -> QuantumCircuit`
Applies unitary basis-change gates to specified qubits immediately before adding $Z$-basis measurement gates:
- `'Z'`: Computational basis (no rotation gates added).
- `'X'`: Hadamard (`h`) gate applied before measurement.
- `'Y'`: S-dagger (`sdg`) followed by Hadamard (`h`) gate applied before measurement.

**Arguments**:
- `circuit` (`QuantumCircuit`): The input circuit.
- `basis` (`str | Sequence[str]`): A single basis character (`'X'`, `'Y'`, `'Z'`) applied to all qubits, a per-qubit string (e.g. `'XZ'`), or a sequence of basis strings (e.g. `['X', 'Z']`). Case-insensitive. Default is `'Z'`.
- `inplace` (`bool`): If `True`, modifies and returns `circuit`. If `False` (default), returns a copy.

**Returns**: `QuantumCircuit` containing measurement operations.

**Raises**:
- `TypeError`: If `circuit` is not a `QuantumCircuit`, `basis` is invalid type, or `inplace` is not a boolean.
- `ValueError`: If `circuit` has 0 qubits, already contains measurement operations, basis string length does not match qubit count, or an unsupported basis is given.

---

### Shot Count & Probability Analysis

Found in `bellbox.measurement`.

#### `analyze_counts(counts: Mapping[str, int]) -> dict[str, Any]`
Validates shot counts and calculates normalized probabilities.

**Arguments**:
- `counts` (`Mapping[str, int]`): Mapping of bitstrings (e.g. `'00'`, `'11'`) to non-negative integer shot counts.

**Returns**: `dict[str, Any]` containing:
- `'total_shots'` (`int`): Sum of all outcome counts.
- `'probabilities'` (`dict[str, float]`): Normalized probabilities sorted lexicographically by bitstring key.

**Raises**:
- `TypeError`: If `counts` is not a `Mapping`, key is not `str`, or count is not `int` (or is `bool`).
- `ValueError`: If bitstring contains invalid characters, length is inconsistent, count is negative, or total count is zero for a non-empty mapping.

#### `counts_to_probabilities(counts: Mapping[str, int]) -> dict[str, float]`
Helper function returning only the `'probabilities'` dictionary from `analyze_counts(counts)`.

#### `is_normalized(probabilities: Mapping[str, float], atol: float = 1e-6) -> bool`
Validates whether probabilities sum to 1.0 within numerical tolerance `atol` and lie in $[0, 1]$.

---

### Two-Qubit Correlation Analysis

Found in `bellbox.measurement`.

#### `calculate_correlations(counts: Mapping[str, int]) -> dict[str, Any]`
Calculates outcome agreement/difference statistics and correlation coefficient $E = P(00) + P(11) - P(01) - P(10)$.

**Arguments**:
- `counts` (`Mapping[str, int]`): Mapping of 2-bit strings to non-negative integer shot counts.

**Returns**: `dict[str, Any]` containing:
- `'total_shots'` (`int`): Total measurement shots.
- `'agree_count'` (`int`): Count of outcomes `'00'` and `'11'`.
- `'agree_probability'` (`float`): Probability $P(00) + P(11)$.
- `'differ_count'` (`int`): Count of outcomes `'01'` and `'10'`.
- `'differ_probability'` (`float`): Probability $P(01) + P(10)$.
- `'correlation'` (`float`): Correlation coefficient $E \in [-1.0, 1.0]$.

**Raises**:
- `TypeError`: If `counts` is not a `Mapping`, key is not `str`, or count is not `int`.
- `ValueError`: If bitstring length is not 2, contains non-binary characters, count is negative, or total shots is 0.

---

### CHSH Bell Inequality Analysis

Found in `bellbox.chsh`.

#### `calculate_chsh(e_ab: float, e_ab_prime: float, e_a_prime_b: float, e_a_prime_b_prime: float, atol: float = 1e-6) -> dict[str, Any]`
Computes the CHSH statistic $S = E(a,b) + E(a,b') + E(a',b) - E(a',b')$ and evaluates classical and quantum bounds.

**Arguments**:
- `e_ab` (`float`): Correlation $E(a, b) \in [-1, 1]$.
- `e_ab_prime` (`float`): Correlation $E(a, b') \in [-1, 1]$.
- `e_a_prime_b` (`float`): Correlation $E(a', b) \in [-1, 1]$.
- `e_a_prime_b_prime` (`float`): Correlation $E(a', b') \in [-1, 1]$.
- `atol` (`float`): Numerical tolerance for bound comparisons (default: `1e-6`).

**Returns**: `dict[str, Any]` containing:
- `'s_value'` (`float`): Signed CHSH parameter $S$.
- `'abs_s_value'` (`float`): Absolute magnitude $|S|$.
- `'classical_bound'` (`float`): Classical local realism bound `2.0`.
- `'tsirelson_bound'` (`float`): Tsirelson quantum upper bound `2 * sqrt(2)` ($\approx 2.828427$).
- `'violates_classical_bound'` (`bool`): `True` if $|S| > 2.0 + \text{atol}$.
- `'within_tsirelson_bound'` (`bool`): `True` if $|S| \le 2\sqrt{2} + \text{atol}$.
- `'correlations'` (`dict[str, float]`): Dictionary mirroring input correlations.

**Raises**:
- `TypeError`: If any correlation or `atol` is not a real number or is a boolean.
- `ValueError`: If `atol` is negative, or if any correlation is NaN, infinite, or outside $[-1, 1]$.

#### Constants
- `CLASSICAL_CHSH_BOUND` (`float = 2.0`)
- `TSIRELSON_CHSH_BOUND` (`float = 2.8284271247461903`)

---

### Circuit Validation Helpers

Found in `bellbox.validation`.

#### `validate_qubit_count(circuit: QuantumCircuit, expected_qubits: int) -> bool`
Returns `True` if `circuit.num_qubits == expected_qubits`.

#### `has_measurements(circuit: QuantumCircuit) -> bool`
Returns `True` if `circuit` contains any `'measure'` gate instructions.

#### `validate_circuit(circuit: QuantumCircuit, expected_qubits: int | None = None, require_measurements: bool = False) -> dict[str, Any]`
Performs structural checks on qubit count and measurement presence.

---

## Example Scripts

The `examples/` directory contains runnable demonstration scripts:

### 1. `examples/bell_states.py`
Demonstrates:
- Constructing all four Bell states ($|\Phi^+\rangle$, $|\Phi^-\rangle$, $|\Psi^+\rangle$, $|\Psi^-\rangle$).
- Inspecting quantum statevectors and theoretical probabilities.
- Structural circuit validation using `validate_circuit`.
- Measuring $|\Phi^+\rangle$ across $Z$, $X$, and $Y$ bases using `measure_in_basis`.

**Run Command**:
```bash
python examples/bell_states.py
```

### 2. `examples/chsh_inequality.py`
Demonstrates:
- Pure mathematical CHSH calculation from four correlation values.
- Quantum circuit simulation for $|\Phi^+\rangle$ using optimal measurement settings ($a=0, a'=\pi/2$, $b=\pi/4, b'=-\pi/4$).
- Comparison of exact quantum statevector probabilities against 10,000-shot finite sampling.
- Explicit scientific context disclaimers.

**Run Command**:
```bash
python examples/chsh_inequality.py
```

---

## Scientific Concepts & Conventions

### Eigenvalue Mapping & Correlation Convention
Single-qubit measurement outcomes $0$ and $1$ map to Pauli $Z$ eigenvalues $+1$ and $-1$, respectively.
For a 2-qubit system measured in outcome $(b_0, b_1) \in \{0, 1\}^2$:
- `'00'` and `'11'`: Outcomes agree $\to (+1)(+1) = (-1)(-1) = +1$.
- `'01'` and `'10'`: Outcomes differ $\to (+1)(-1) = (-1)(+1) = -1$.

The expectation value / correlation coefficient is:
$$E = P(00) + P(11) - P(01) - P(10)$$

### CHSH Bell Inequality
The CHSH statistic evaluates local realism across four measurement settings:
$$S = E(a, b) + E(a, b') + E(a', b) - E(a', b')$$

- **Classical Bound**: Local hidden-variable theories require $|S| \le 2.0$.
- **Tsirelson Bound**: Quantum mechanics permits maximal violation up to $|S| = 2\sqrt{2} \approx 2.828427$.

### Simulation vs Physical Hardware Proof
Ideal noiseless simulator results prove theoretical quantum model predictions, but do **not** constitute physical experimental proof (which requires physical hardware, detector efficiency calibration, and statistical error analysis).

---

## Development and Testing

### Running Unit Tests
Execute the complete test suite via `pytest`:
```bash
python -m pytest
```

### Running Lint Checks
Enforce style guidelines and lint checks using `ruff`:
```bash
python -m ruff check .
```

---

## Limitations

- **State Preparation**: Helper constructors focus on 2-qubit Bell states.
- **Single-Basis Rotations**: `measure_in_basis` supports Pauli $X, Y, Z$ bases. Arbitrary measurement angles require explicit gate rotations (e.g. $R_y(\theta)$ as shown in `examples/chsh_inequality.py`).
- **Hardware Execution**: BellBox targets local circuit construction and simulation backend inspection; it does not execute circuits on physical quantum hardware backends.

---

## License

BellBox is licensed under the [MIT License](LICENSE).
