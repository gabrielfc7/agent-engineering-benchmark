"""Tests for symbolic verification engine and math string parser."""

import pytest
import sympy as sp
from agent_benchmark.symbolic import SymbolicVerifier, clean_math_string, parse_symbolic_expression


def test_clean_math_string():
    """Verify markdown and LaTeX math stripping."""
    raw = "```python\n\\frac{P \\cdot L^3}{3 E I}\n```"
    cleaned = clean_math_string(raw)
    assert "\\frac" not in cleaned
    assert "\\cdot" not in cleaned


def test_symbolic_equivalence_polynomial_and_algebra():
    """Verify algebraic identities where string representations differ."""
    # Difference of squares
    assert SymbolicVerifier.verify_equivalence("(x - 1)*(x + 1)", "x**2 - 1")
    # Factored vs expanded
    assert SymbolicVerifier.verify_equivalence("(a + b)**2", "a**2 + 2*a*b + b**2")
    # Engineering beam formula variants
    assert SymbolicVerifier.verify_equivalence("(P * L**3) / (3 * E * I)", "(1/3) * (P / E) * (L**3 / I)")


def test_symbolic_equivalence_trigonometric_and_exponential():
    """Verify trigonometric and exponential identities."""
    # Double angle formula
    assert SymbolicVerifier.verify_equivalence("sin(2*x)", "2*sin(x)*cos(x)")
    # Exponential product
    assert SymbolicVerifier.verify_equivalence("exp(a) * exp(b)", "exp(a + b)")
    # Pythagorean trigonometric identity
    assert SymbolicVerifier.verify_equivalence("sin(x)**2 + cos(x)**2", "1")


def test_symbolic_non_equivalence():
    """Verify that genuinely different mathematical expressions are rejected."""
    assert not SymbolicVerifier.verify_equivalence("x**2 + 1", "x**2 - 1")
    assert not SymbolicVerifier.verify_equivalence("(P * L**2) / (2 * E * I)", "(P * L**3) / (3 * E * I)")


def test_equation_equivalence():
    """Verify equivalence between algebraic equations up to non-zero scalar factor."""
    assert SymbolicVerifier.verify_equation_equivalence("2*x + 4*y = 10", "x + 2*y = 5")
    assert SymbolicVerifier.verify_equation_equivalence("F - m*a = 0", "F = m*a")
