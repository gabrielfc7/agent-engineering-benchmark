"""Tests for physical dimensions representation and dimensional homogeneity verification."""

import pytest
from agent_benchmark.dimensional import (
    ACCELERATION,
    ENERGY,
    FORCE,
    MASS,
    PRESSURE,
    VELOCITY,
    DimensionVector,
    DimensionalChecker,
    DimensionalHomogeneityError,
)


def test_dimension_vector_algebra():
    """Verify algebraic properties of SI dimension vectors."""
    # F = m * a -> [M][L][T]^-2
    f = MASS * ACCELERATION
    assert f == FORCE
    assert f.m == 1 and f.l == 1 and f.t == -2

    # Pressure = Force / Area -> [M][L]^-1[T]^-2
    p = f / (DimensionVector(l=1) ** 2)
    assert p == PRESSURE
    assert p.m == 1 and p.l == -1 and p.t == -2

    # Kinetic energy = Force * Length -> [M][L]^2[T]^-2
    e = f * DimensionVector(l=1)
    assert e == ENERGY


def test_dimensional_inference_valid():
    """Verify dimensional inference on valid physical expressions."""
    sym_dims = {
        "P": "force",
        "L": "length",
        "E": "pressure",
        "I": DimensionVector(l=4),  # Second moment of area [L]^4
    }

    # Bending moment M = P * L -> Energy / Torque [M][L]^2[T]^-2
    dim_m = DimensionalChecker.infer_dimension("P * L", sym_dims)
    assert dim_m == ENERGY

    # Tip deflection delta = (P * L**3) / (3 * E * I) -> Length [L]
    dim_delta = DimensionalChecker.infer_dimension("(P * L**3) / (3 * E * I)", sym_dims)
    assert dim_delta == DimensionVector(l=1)


def test_dimensional_homogeneity_violation_addition():
    """Verify error raised when adding quantities with mismatched dimensions."""
    sym_dims = {
        "F": "force",
        "v": "velocity",
    }
    with pytest.raises(DimensionalHomogeneityError, match="Dimensional mismatch"):
        DimensionalChecker.infer_dimension("F + v", sym_dims)


def test_dimensional_homogeneity_violation_transcendental():
    """Verify error raised when transcendental function receives dimensionful argument."""
    sym_dims = {
        "x": "length",
    }
    with pytest.raises(DimensionalHomogeneityError, match="must be dimensionless"):
        DimensionalChecker.infer_dimension("sin(x)", sym_dims)
