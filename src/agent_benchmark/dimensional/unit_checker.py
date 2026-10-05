"""Dimensional homogeneity and physical unit consistency verification engine."""

from __future__ import annotations

import sympy as sp

from agent_benchmark.dimensional.dimensions import (
    DIMENSIONLESS,
    DimensionVector,
    lookup_dimension,
)
from agent_benchmark.symbolic.parser import parse_symbolic_expression


class DimensionalHomogeneityError(ValueError):
    """Raised when an equation or expression violates dimensional homogeneity."""
    pass


class DimensionalChecker:
    """Verifies dimensional homogeneity across multi-step symbolic derivations."""

    @classmethod
    def infer_dimension(
        cls,
        expr: sp.Expr | str,
        symbol_dimensions: dict[str, DimensionVector | str],
    ) -> DimensionVector:
        """Infer dimension vector of an expression and assert internal homogeneity.

        Parameters
        ----------
        expr : sp.Expr | str
            Symbolic expression or string.
        symbol_dimensions : dict[str, DimensionVector | str]
            Mapping of symbol name strings to their respective DimensionVector or dimension string names.
        """
        if isinstance(expr, str):
            local_syms = {str(k): sp.Symbol(str(k)) for k in symbol_dimensions.keys()}
            expr = parse_symbolic_expression(expr, local_dict=local_syms)

        # Standardize symbol dimensions mapping
        dims_map: dict[str, DimensionVector] = {}
        for k, v in symbol_dimensions.items():
            dims_map[str(k)] = lookup_dimension(v) if isinstance(v, str) else v

        return cls._infer_recursive(expr, dims_map)

    @classmethod
    def _infer_recursive(cls, node: sp.Basic, dims: dict[str, DimensionVector]) -> DimensionVector:
        # 1. Pure numbers and floats are dimensionless
        if node.is_Number:
            return DIMENSIONLESS

        # 2. Symbols
        if isinstance(node, sp.Symbol):
            sym_name = str(node.name)
            if sym_name not in dims:
                # Default unknown symbols to dimensionless
                return DIMENSIONLESS
            return dims[sym_name]

        # 3. Addition / Subtraction: All terms must have identical dimensions
        if isinstance(node, sp.Add):
            args = node.args
            first_dim = cls._infer_recursive(args[0], dims)
            for other_arg in args[1:]:
                other_dim = cls._infer_recursive(other_arg, dims)
                if first_dim != other_dim:
                    raise DimensionalHomogeneityError(
                        f"Dimensional mismatch in addition: '{args[0]}' has {first_dim.to_symbolic_string()} "
                        f"but '{other_arg}' has {other_dim.to_symbolic_string()}."
                    )
            return first_dim

        # 4. Multiplication / Division
        if isinstance(node, sp.Mul):
            res = DIMENSIONLESS
            for factor in node.args:
                res = res * cls._infer_recursive(factor, dims)
            return res

        # 5. Powers
        if isinstance(node, sp.Pow):
            base, exponent = node.args
            exp_dim = cls._infer_recursive(exponent, dims)
            if not exp_dim.is_dimensionless():
                raise DimensionalHomogeneityError(
                    f"Exponent '{exponent}' must be dimensionless, got {exp_dim.to_symbolic_string()}."
                )

            base_dim = cls._infer_recursive(base, dims)
            if exponent.is_Integer:
                return base_dim ** int(exponent)
            elif exponent.is_Rational:
                # Support fractional powers if dimensions are divisible
                num, den = int(exponent.p), int(exponent.q)
                for exp_val, name in [
                    (base_dim.m, "m"),
                    (base_dim.l, "l"),
                    (base_dim.t, "t"),
                    (base_dim.theta, "theta"),
                    (base_dim.i, "i"),
                    (base_dim.n, "n"),
                    (base_dim.j, "j"),
                ]:
                    if (exp_val * num) % den != 0:
                        raise DimensionalHomogeneityError(
                            f"Fractional power {exponent} produces non-integer physical dimension on {name}."
                        )
                return DimensionVector(
                    m=(base_dim.m * num) // den,
                    l=(base_dim.l * num) // den,
                    t=(base_dim.t * num) // den,
                    theta=(base_dim.theta * num) // den,
                    i=(base_dim.i * num) // den,
                    n=(base_dim.n * num) // den,
                    j=(base_dim.j * num) // den,
                )
            else:
                if not base_dim.is_dimensionless():
                    raise DimensionalHomogeneityError("Dimensionful base raised to non-rational exponent.")
                return DIMENSIONLESS

        # 6. Transcendental and trigonometric functions
        if isinstance(node, sp.Function):
            # Arguments to sin, cos, exp, log, tan, etc. MUST be dimensionless
            for arg in node.args:
                arg_dim = cls._infer_recursive(arg, dims)
                if not arg_dim.is_dimensionless():
                    raise DimensionalHomogeneityError(
                        f"Argument to function '{node.func.__name__}' must be dimensionless, "
                        f"got {arg_dim.to_symbolic_string()}."
                    )
            return DIMENSIONLESS

        return DIMENSIONLESS

    @classmethod
    def check_equation_homogeneity(
        cls,
        lhs: sp.Expr | str,
        rhs: sp.Expr | str,
        symbol_dimensions: dict[str, DimensionVector | str],
    ) -> bool:
        """Check if LHS and RHS of an equation share identical dimensions."""
        try:
            dim_lhs = cls.infer_dimension(lhs, symbol_dimensions)
            dim_rhs = cls.infer_dimension(rhs, symbol_dimensions)
            return dim_lhs == dim_rhs
        except DimensionalHomogeneityError:
            return False
