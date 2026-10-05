"""Curated engineering benchmark test suite of multi-step problems."""

from __future__ import annotations

from agent_benchmark.harness.problem import EngineeringProblem, EngineeringStep


def get_standard_engineering_suite() -> list[EngineeringProblem]:
    """Retrieve the standard 5-problem engineering benchmark suite."""
    return [
        EngineeringProblem(
            problem_id="ENG-STR-01",
            title="Cantilever Beam Deflection and Peak Bending Stress",
            domain="Structural Mechanics",
            problem_statement=(
                "A cantilever beam of length L is subjected to a vertical point load P at its free tip. "
                "Derive the maximum bending moment at the fixed support, the maximum bending stress "
                "for a section with distance c from the neutral axis and second moment of area I, "
                "and the maximum tip deflection using Euler-Bernoulli beam theory with elastic modulus E."
            ),
            symbol_dimensions={
                "P": "force",
                "L": "length",
                "c": "length",
                "I": "length",  # Note: I is L^4, but length^4 can be checked
                "E": "pressure",
                "M": "energy",
                "sigma": "pressure",
                "delta": "length",
            },
            steps=[
                EngineeringStep(
                    step_number=1,
                    description="Maximum bending moment at fixed support root: M = P * L",
                    target_symbolic="P * L",
                    expected_dimension="energy",
                    expected_numeric=5000.0,  # P=1000 N, L=5 m -> 5000 N*m
                ),
                EngineeringStep(
                    step_number=2,
                    description="Peak outer-fiber bending stress: sigma = (P * L * c) / I",
                    target_symbolic="(P * L * c) / I",
                    expected_dimension="pressure",
                ),
                EngineeringStep(
                    step_number=3,
                    description="Maximum tip deflection: delta = (P * L**3) / (3 * E * I)",
                    target_symbolic="(P * L**3) / (3 * E * I)",
                    expected_dimension="length",
                ),
            ],
            final_symbolic="(P * L**3) / (3 * E * I)",
            final_numeric=0.0125,
        ),
        EngineeringProblem(
            problem_id="ENG-FLD-02",
            title="Pipe Flow Reynolds Number and Laminar Friction Factor",
            domain="Fluid Mechanics",
            problem_statement=(
                "Fluid of density rho and dynamic viscosity mu flows through a circular pipe of inner diameter D "
                "at volumetric flow rate Q. Derive the mean flow velocity v, the Reynolds number Re, and the Darcy "
                "friction factor f under laminar flow conditions."
            ),
            symbol_dimensions={
                "rho": "density",
                "mu": "dynamic_viscosity",
                "D": "length",
                "Q": "power",  # volumetric flow rate m^3/s
                "v": "velocity",
                "Re": "dimensionless",
                "f": "dimensionless",
            },
            steps=[
                EngineeringStep(
                    step_number=1,
                    description="Mean flow velocity: v = (4 * Q) / (pi * D**2)",
                    target_symbolic="(4 * Q) / (pi * D**2)",
                    expected_dimension="velocity",
                ),
                EngineeringStep(
                    step_number=2,
                    description="Reynolds number: Re = (rho * v * D) / mu",
                    target_symbolic="(rho * v * D) / mu",
                    expected_dimension="dimensionless",
                ),
                EngineeringStep(
                    step_number=3,
                    description="Darcy-Weisbach laminar friction factor: f = 64 / Re",
                    target_symbolic="64 / Re",
                    expected_dimension="dimensionless",
                ),
            ],
            final_symbolic="64 / Re",
            final_numeric=0.04,
        ),
        EngineeringProblem(
            problem_id="ENG-THM-03",
            title="Gibbs Free Energy and Chemical Equilibrium Constant",
            domain="Thermodynamics",
            problem_statement=(
                "For a chemical reaction at absolute temperature T with standard enthalpy change dH and entropy change dS, "
                "derive the standard Gibbs free energy change dG and the chemical equilibrium constant K with universal gas constant R."
            ),
            symbol_dimensions={
                "dH": "energy",
                "dS": "heat_capacity",
                "T": "temperature",
                "dG": "energy",
                "R": "heat_capacity",
                "K": "dimensionless",
            },
            steps=[
                EngineeringStep(
                    step_number=1,
                    description="Standard Gibbs free energy: dG = dH - T * dS",
                    target_symbolic="dH - T * dS",
                    expected_dimension="energy",
                ),
                EngineeringStep(
                    step_number=2,
                    description="Equilibrium constant: K = exp(-dG / (R * T))",
                    target_symbolic="exp(-dG / (R * T))",
                    expected_dimension="dimensionless",
                ),
            ],
            final_symbolic="exp(-(dH - T * dS) / (R * T))",
            final_numeric=1.45,
        ),
        EngineeringProblem(
            problem_id="ENG-ELE-04",
            title="Series RLC Resonant Frequency and Quality Factor",
            domain="Electrical Engineering",
            problem_statement=(
                "For a series RLC circuit with resistance R, inductance L, and capacitance C, derive the undamped "
                "angular resonant frequency omega_0 and the dimensionless quality factor Q."
            ),
            symbol_dimensions={
                "R": "resistance",
                "L": "inductance",
                "C": "capacitance",
                "omega_0": "frequency",
                "Q": "dimensionless",
            },
            steps=[
                EngineeringStep(
                    step_number=1,
                    description="Undamped resonant frequency: omega_0 = 1 / sqrt(L * C)",
                    target_symbolic="1 / sqrt(L * C)",
                    expected_dimension="frequency",
                ),
                EngineeringStep(
                    step_number=2,
                    description="Quality factor: Q = (omega_0 * L) / R",
                    target_symbolic="(1 / R) * sqrt(L / C)",
                    expected_dimension="dimensionless",
                ),
            ],
            final_symbolic="(1 / R) * sqrt(L / C)",
            final_numeric=10.0,
        ),
        EngineeringProblem(
            problem_id="ENG-CTRL-05",
            title="Underdamped Second-Order System Frequency and Damping Decrement",
            domain="Dynamics & Control",
            problem_statement=(
                "For an underdamped second-order mechanical oscillator with undamped natural frequency omega_n and "
                "damping ratio zeta in (0, 1), derive the damped natural frequency omega_d and the logarithmic decrement delta."
            ),
            symbol_dimensions={
                "omega_n": "frequency",
                "zeta": "dimensionless",
                "omega_d": "frequency",
                "delta": "dimensionless",
            },
            steps=[
                EngineeringStep(
                    step_number=1,
                    description="Damped natural frequency: omega_d = omega_n * sqrt(1 - zeta**2)",
                    target_symbolic="omega_n * sqrt(1 - zeta**2)",
                    expected_dimension="frequency",
                ),
                EngineeringStep(
                    step_number=2,
                    description="Logarithmic decrement: delta = (2 * pi * zeta) / sqrt(1 - zeta**2)",
                    target_symbolic="(2 * pi * zeta) / sqrt(1 - zeta**2)",
                    expected_dimension="dimensionless",
                ),
            ],
            final_symbolic="(2 * pi * zeta) / sqrt(1 - zeta**2)",
            final_numeric=0.64,
        ),
    ]
