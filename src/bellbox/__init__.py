"""BellBox: Quantum circuit experiments and educational tools."""

from bellbox.chsh import (
    CLASSICAL_CHSH_BOUND,
    TSIRELSON_CHSH_BOUND,
    calculate_chsh,
)
from bellbox.measurement import (
    analyze_counts,
    calculate_correlations,
    counts_to_probabilities,
    is_normalized,
    measure_in_basis,
)
from bellbox.states import phi_minus, phi_plus, psi_minus, psi_plus
from bellbox.validation import (
    has_measurements,
    validate_circuit,
    validate_qubit_count,
)

__version__ = "0.1.0"

__all__ = [
    "phi_plus",
    "phi_minus",
    "psi_plus",
    "psi_minus",
    "analyze_counts",
    "calculate_correlations",
    "counts_to_probabilities",
    "is_normalized",
    "measure_in_basis",
    "calculate_chsh",
    "CLASSICAL_CHSH_BOUND",
    "TSIRELSON_CHSH_BOUND",
    "validate_qubit_count",
    "has_measurements",
    "validate_circuit",
]


