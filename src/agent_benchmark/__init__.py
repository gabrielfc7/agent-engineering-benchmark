"""Autonomous Agent Benchmark Harness for Engineering Systems."""

from agent_benchmark.dimensional import (
    DimensionVector,
    DimensionalChecker,
    DimensionalHomogeneityError,
    lookup_dimension,
)
from agent_benchmark.harness import (
    AgentProblemAttempt,
    AgentStepResponse,
    BenchmarkEvaluator,
    EngineeringProblem,
    EngineeringStep,
    ProblemEvaluation,
    StepEvaluation,
    get_standard_engineering_suite,
)
from agent_benchmark.symbolic import (
    SymbolicVerifier,
    clean_math_string,
    parse_symbolic_expression,
)
from agent_benchmark.telemetry import (
    BenchmarkReporter,
    BenchmarkSummary,
    calculate_pass_at_k,
    compute_benchmark_summary,
)

__version__ = "0.1.0"

__all__ = [
    # Symbolic
    "clean_math_string",
    "parse_symbolic_expression",
    "SymbolicVerifier",
    # Dimensional
    "DimensionVector",
    "DimensionalChecker",
    "DimensionalHomogeneityError",
    "lookup_dimension",
    # Harness
    "EngineeringStep",
    "EngineeringProblem",
    "AgentStepResponse",
    "AgentProblemAttempt",
    "StepEvaluation",
    "ProblemEvaluation",
    "BenchmarkEvaluator",
    "get_standard_engineering_suite",
    # Telemetry
    "calculate_pass_at_k",
    "BenchmarkSummary",
    "compute_benchmark_summary",
    "BenchmarkReporter",
]
