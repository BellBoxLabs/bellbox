# Contributing to BellBox

Thank you for your interest in contributing to **BellBox**! This project aims to provide approachable, maintainable, and educational quantum computing utilities.

---

## Local Development Setup

To set up a local development environment:

1. **Navigate to the repository directory**:
   ```bash
   cd qubitlab
   ```

2. **Create and activate a virtual environment**:
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

3. **Install BellBox in editable mode with development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

---

## Coding Conventions

- **Python Version**: Target Python 3.10 or higher.
- **Style Guide**: Follow PEP 8 guidelines. Code formatting and linting are enforced via [Ruff](https://github.com/astral-sh/ruff).
- **Type Annotations**: Add type hints for all public functions, arguments, and return values.
- **Docstrings**: Provide clear, descriptive docstrings explaining mathematical background, argument types, return types, and possible exceptions.
- **Modular Design**: Keep modules focused and concise. Avoid giant classes or unnecessary abstractions.

---

## Testing Requirements

- Write unit tests for all new functions and edge cases using `pytest`.
- **Deterministic Tests**: Use exact quantum statevector analysis (`Statevector`) for testing quantum states and theoretical probabilities rather than relying on non-deterministic shot simulations.
- Ensure all tests pass before submitting changes:
  ```bash
  pytest
  ```

---

## Linting and Code Quality

Run Ruff to inspect and format your code:

- **Check for lint errors**:
  ```bash
  ruff check .
  ```
- **Auto-fix lint errors**:
  ```bash
  ruff check --fix .
  ```

---

## Workflow for Adding Features

1. Write clean, documented implementation code in `src/bellbox/`.
2. Add comprehensive unit tests in `tests/`.
3. Verify test coverage and pass all lint checks.
4. Update examples in `examples/` if introducing new public functionality.
