from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DimensionVector:
    """7-dimensional base SI physical dimension vector: [M, L, T, Theta, I, N, J]."""

    m: int = 0      # Mass (kg)
    l: int = 0      # Length (m)
    t: int = 0      # Time (s)
    theta: int = 0  # Thermodynamic Temperature (K)
    i: int = 0      # Electric Current (A)
    n: int = 0      # Amount of Substance (mol)
    j: int = 0      # Luminous Intensity (cd)

    def is_dimensionless(self) -> bool:
        return (
            self.m == 0
            and self.l == 0
            and self.t == 0
            and self.theta == 0
            and self.i == 0
            and self.n == 0
            and self.j == 0
        )

    def __mul__(self, other: DimensionVector) -> DimensionVector:
        return DimensionVector(
            m=self.m + other.m,
            l=self.l + other.l,
            t=self.t + other.t,
            theta=self.theta + other.theta,
            i=self.i + other.i,
            n=self.n + other.n,
            j=self.j + other.j,
        )

    def __truediv__(self, other: DimensionVector) -> DimensionVector:
        return DimensionVector(
            m=self.m - other.m,
            l=self.l - other.l,
            t=self.t - other.t,
            theta=self.theta - other.theta,
            i=self.i - other.i,
            n=self.n - other.n,
            j=self.j - other.j,
        )

    def __pow__(self, power: int) -> DimensionVector:
        if not isinstance(power, int):
            raise TypeError("Dimension powers must be integer exponents.")
        return DimensionVector(
            m=self.m * power,
            l=self.l * power,
            t=self.t * power,
            theta=self.theta * power,
            i=self.i * power,
            n=self.n * power,
            j=self.j * power,
        )

    def to_symbolic_string(self) -> str:
        """Formatted string representation e.g. [M][L]^2[T]^-2."""
        if self.is_dimensionless():
            return "[1] (Dimensionless)"
        parts = []
        names = [("M", self.m), ("L", self.l), ("T", self.t), ("Theta", self.theta), ("I", self.i), ("N", self.n), ("J", self.j)]
        for sym, exp in names:
            if exp == 1:
                parts.append(f"[{sym}]")
            elif exp != 0:
                parts.append(f"[{sym}]^{exp}")
        return "".join(parts)


# Predefined standard physical dimensions
DIMENSIONLESS = DimensionVector()
MASS = DimensionVector(m=1)
LENGTH = DimensionVector(l=1)
TIME = DimensionVector(t=1)
TEMPERATURE = DimensionVector(theta=1)
CURRENT = DimensionVector(i=1)
AMOUNT = DimensionVector(n=1)
LUMINOUS = DimensionVector(j=1)

# Kinematics & Mechanics
AREA = LENGTH ** 2
VOLUME = LENGTH ** 3
VELOCITY = LENGTH / TIME
ACCELERATION = VELOCITY / TIME
FORCE = MASS * ACCELERATION                     # [M][L][T]^-2 (Newton)
ENERGY = FORCE * LENGTH                         # [M][L]^2[T]^-2 (Joule)
POWER = ENERGY / TIME                           # [M][L]^2[T]^-3 (Watt)
PRESSURE = FORCE / AREA                         # [M][L]^-1[T]^-2 (Pascal)
DENSITY = MASS / VOLUME                         # [M][L]^-3
DYNAMIC_VISCOSITY = PRESSURE * TIME             # [M][L]^-1[T]^-1 (Pa*s)
KINEMATIC_VISCOSITY = DYNAMIC_VISCOSITY / DENSITY  # [L]^2[T]^-1 (m^2/s)
FREQUENCY = TIME ** -1                          # [T]^-1 (Hz)

# Electromagnetism
CHARGE = CURRENT * TIME                         # [I][T] (Coulomb)
VOLTAGE = POWER / CURRENT                       # [M][L]^2[T]^-3[I]^-1 (Volt)
RESISTANCE = VOLTAGE / CURRENT                  # [M][L]^2[T]^-3[I]^-2 (Ohm)
CAPACITANCE = CHARGE / VOLTAGE                  # [M]^-1[L]^-2[T]^4[I]^2 (Farad)
INDUCTANCE = VOLTAGE * TIME / CURRENT           # [M][L]^2[T]^-2[I]^-2 (Henry)

# Thermodynamics
HEAT_CAPACITY = ENERGY / TEMPERATURE            # [M][L]^2[T]^-2[Theta]^-1 (J/K)
SPECIFIC_HEAT = HEAT_CAPACITY / MASS            # [L]^2[T]^-2[Theta]^-1 (J/(kg*K))
MOLAR_ENERGY = ENERGY / AMOUNT                  # [M][L]^2[T]^-2[N]^-1 (J/mol)

STANDARD_DIMENSIONS: dict[str, DimensionVector] = {
    "dimensionless": DIMENSIONLESS,
    "mass": MASS,
    "length": LENGTH,
    "time": TIME,
    "temperature": TEMPERATURE,
    "current": CURRENT,
    "velocity": VELOCITY,
    "acceleration": ACCELERATION,
    "force": FORCE,
    "energy": ENERGY,
    "work": ENERGY,
    "heat": ENERGY,
    "power": POWER,
    "pressure": PRESSURE,
    "stress": PRESSURE,
    "density": DENSITY,
    "dynamic_viscosity": DYNAMIC_VISCOSITY,
    "kinematic_viscosity": KINEMATIC_VISCOSITY,
    "frequency": FREQUENCY,
    "voltage": VOLTAGE,
    "resistance": RESISTANCE,
    "capacitance": CAPACITANCE,
    "inductance": INDUCTANCE,
    "heat_capacity": HEAT_CAPACITY,
    "specific_heat": SPECIFIC_HEAT,
    "molar_energy": MOLAR_ENERGY,
}


def lookup_dimension(name: str) -> DimensionVector:
    """Resolve dimension name to DimensionVector."""
    clean = name.strip().lower().replace("-", "_").replace(" ", "_")
    if clean in STANDARD_DIMENSIONS:
        return STANDARD_DIMENSIONS[clean]
    raise KeyError(f"Unknown physical dimension '{name}'. Available: {list(STANDARD_DIMENSIONS.keys())}")
