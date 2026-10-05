"""Safe mathematical parsing of candidate LLM strings into SymPy symbolic expressions."""

from __future__ import annotations

import re
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

TRANSFORMATIONS = standard_transformations + (
    convert_xor,
    implicit_multiplication_application,
)


def clean_math_string(expr_str: str) -> str:
    """Preprocess raw LLM output string to standard Python/SymPy syntax."""
    s = expr_str.strip()
    # Strip markdown backticks and LaTeX math wrappers
    s = re.sub(r"^```(?:python|math|latex)?", "", s, flags=re.IGNORECASE)
    s = re.sub(r"```$", "", s)
    s = s.strip("$ \t\n\r")

    # Common LaTeX replacements
    s = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", s)
    s = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", s)
    s = re.sub(r"\\cdot", "*", s)
    s = re.sub(r"\\times", "*", s)
    s = re.sub(r"\\pi", "pi", s)
    s = re.sub(r"\\sin", "sin", s)
    s = re.sub(r"\\cos", "cos", s)
    s = re.sub(r"\\exp", "exp", s)
    s = re.sub(r"\\ln", "log", s)

    # Remove escaped brackets
    s = s.replace(r"\{", "(").replace(r"\}", ")")
    s = s.replace(r"\[", "(").replace(r"\]", ")")

    # Replace caret with power if any remain
    s = s.replace("^", "**")
    return s.strip()


DEFAULT_ENGINEERING_SYMBOLS: dict[str, sp.Symbol] = {
    # Capital letters reserved by SymPy
    "E": sp.Symbol("E"),
    "I": sp.Symbol("I"),
    "N": sp.Symbol("N"),
    "S": sp.Symbol("S"),
    "O": sp.Symbol("O"),
    "C": sp.Symbol("C"),
    "Q": sp.Symbol("Q"),
    "R": sp.Symbol("R"),
    "T": sp.Symbol("T"),
    # Greek letters that collide with SymPy functions (e.g. Riemann zeta, Gamma fn)
    "zeta": sp.Symbol("zeta"),
    "gamma": sp.Symbol("gamma"),
    "beta": sp.Symbol("beta"),
    "delta": sp.Symbol("delta"),
    "theta": sp.Symbol("theta"),
    "eta": sp.Symbol("eta"),
    "mu": sp.Symbol("mu"),
    "nu": sp.Symbol("nu"),
    "rho": sp.Symbol("rho"),
    "sigma": sp.Symbol("sigma"),
    "tau": sp.Symbol("tau"),
    "phi": sp.Symbol("phi"),
    "psi": sp.Symbol("psi"),
    "omega": sp.Symbol("omega"),
    "omega_n": sp.Symbol("omega_n"),
    "omega_d": sp.Symbol("omega_d"),
}


def parse_symbolic_expression(expr_str: str, local_dict: dict[str, sp.Symbol] | None = None) -> sp.Expr:
    """Safely parse mathematical expression string into SymPy Expr.

    Parameters
    ----------
    expr_str : str
        Mathematical expression string.
    local_dict : dict[str, Symbol], optional
        Symbol dictionary with specific assumptions.

    Returns
    -------
    sp.Expr
        Parsed SymPy expression.
    """
    cleaned = clean_math_string(expr_str)
    if not cleaned:
        raise ValueError("Cannot parse empty mathematical expression.")

    locals_merged = {**DEFAULT_ENGINEERING_SYMBOLS}
    if local_dict is not None:
        locals_merged.update(local_dict)

    try:
        parsed = parse_expr(
            cleaned,
            local_dict=locals_merged,
            transformations=TRANSFORMATIONS,
            evaluate=True,
        )
        return parsed
    except Exception as e:
        raise ValueError(f"Failed to parse mathematical expression '{expr_str}': {e}") from e
