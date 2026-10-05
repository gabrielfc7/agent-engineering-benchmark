"""Symbolic verification engine testing mathematical and algebraic equivalence via SymPy."""

from __future__ import annotations

from typing import Sequence
import numpy as np
import sympy as sp

from agent_benchmark.symbolic.parser import parse_symbolic_expression


class SymbolicVerifier:
    """Verifies rigorous mathematical equivalence between candidate LLM responses and ground truths."""

    @classmethod
    def verify_equivalence(
        cls,
        candidate: str | sp.Expr,
        ground_truth: str | sp.Expr,
        tolerance: float = 1e-7,
        n_random_evals: int = 7,
    ) -> bool:
        """Check if candidate and ground truth represent identical mathematical expressions.

        Uses algebraic simplification, polynomial expansion, trigonometric identities,
        and Schwartz-Zippel randomized sampling.
        """
        try:
            cand_expr = parse_symbolic_expression(candidate) if isinstance(candidate, str) else candidate
            gt_expr = parse_symbolic_expression(ground_truth) if isinstance(ground_truth, str) else ground_truth
        except Exception:
            return False

        if cand_expr == gt_expr:
            return True

        diff = cand_expr - gt_expr

        # 1. Direct simplification
        try:
            if sp.simplify(diff) == 0:
                return True
        except Exception:
            pass

        # 2. Polynomial expansion
        try:
            if sp.expand(diff) == 0:
                return True
        except Exception:
            pass

        # 3. Trigonometric simplification
        try:
            if sp.trigsimp(diff) == 0:
                return True
        except Exception:
            pass

        # 4. Rational cancellation
        try:
            if sp.cancel(diff) == 0:
                return True
        except Exception:
            pass

        # 5. Factored difference
        try:
            if sp.factor(diff) == 0:
                return True
        except Exception:
            pass

        # 6. Randomized numerical evaluation (Schwartz-Zippel testing on free symbols)
        symbols = list(diff.free_symbols)
        if not symbols:
            # Constant difference
            try:
                return abs(complex(diff.evalf())) < tolerance
            except Exception:
                return False

        rng = np.random.default_rng(1337)
        for _ in range(n_random_evals):
            # Sample strictly positive reals away from 0 and 1 to avoid trivial roots / singularities
            subs_dict = {sym: float(rng.uniform(1.5, 8.5)) for sym in symbols}
            try:
                val = complex(diff.evalf(subs=subs_dict))
                if abs(val) > tolerance:
                    return False
            except Exception:
                return False

        return True

    @classmethod
    def verify_equation_equivalence(
        cls,
        cand_eq_str: str,
        gt_eq_str: str,
        tolerance: float = 1e-7,
    ) -> bool:
        """Check if two equations LHS = RHS are mathematically equivalent up to non-zero scalar."""
        def split_eq(s: str) -> tuple[str, str]:
            if "=" in s:
                parts = s.split("=", 1)
                return parts[0].strip(), parts[1].strip()
            return s.strip(), "0"

        c_lhs, c_rhs = split_eq(cand_eq_str)
        g_lhs, g_rhs = split_eq(gt_eq_str)

        try:
            c_diff = parse_symbolic_expression(c_lhs) - parse_symbolic_expression(c_rhs)
            g_diff = parse_symbolic_expression(g_lhs) - parse_symbolic_expression(g_rhs)
        except Exception:
            return False

        # If identical
        if cls.verify_equivalence(c_diff, g_diff, tolerance=tolerance):
            return True

        # Check if proportional: c_diff / g_diff is constant non-zero
        try:
            ratio = sp.simplify(c_diff / g_diff)
            if ratio.is_number and ratio != 0:
                return True
        except Exception:
            pass

        return False
