"""Evaluation engine executing multi-step verification and error classification."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from agent_benchmark.dimensional.unit_checker import DimensionalChecker
from agent_benchmark.harness.problem import (
    AgentProblemAttempt,
    EngineeringProblem,
)
from agent_benchmark.symbolic.verifier import SymbolicVerifier


@dataclass
class StepEvaluation:
    """Detailed verification outcome for an individual reasoning step."""

    step_number: int
    symbolic_correct: bool
    dimensional_correct: bool
    numeric_correct: bool
    error_category: str  # 'NONE', 'SYMBOLIC_MISMATCH', 'DIMENSIONAL_VIOLATION', 'ARITHMETIC_ERROR', 'MISSING_RESPONSE'


@dataclass
class ProblemEvaluation:
    """Consolidated evaluation for an entire multi-step engineering problem."""

    problem_id: str
    all_steps_correct: bool
    final_answer_correct: bool
    step_results: list[StepEvaluation]
    total_steps: int
    correct_steps_count: int
    hallucination_count: int
    reasoning_tokens: int


class BenchmarkEvaluator:
    """Automated benchmark evaluator assessing symbolic accuracy, dimensional validity, and tokens."""

    @classmethod
    def evaluate_attempt(
        cls,
        problem: EngineeringProblem,
        attempt: AgentProblemAttempt,
    ) -> ProblemEvaluation:
        """Evaluate an agent's attempt on a specific engineering problem."""
        step_resp_map = {sr.step_number: sr for sr in attempt.step_responses}
        step_evals: list[StepEvaluation] = []

        for step in problem.steps:
            resp = step_resp_map.get(step.step_number)
            if resp is None or (resp.candidate_symbolic is None and resp.candidate_numeric is None):
                step_evals.append(
                    StepEvaluation(
                        step_number=step.step_number,
                        symbolic_correct=False,
                        dimensional_correct=False,
                        numeric_correct=False,
                        error_category="MISSING_RESPONSE",
                    )
                )
                continue

            # 1. Check Symbolic Equivalence
            symbolic_ok = False
            if resp.candidate_symbolic:
                symbolic_ok = SymbolicVerifier.verify_equivalence(
                    candidate=resp.candidate_symbolic,
                    ground_truth=step.target_symbolic,
                )

            # 2. Check Dimensional Homogeneity
            dim_ok = True
            if resp.candidate_symbolic and step.expected_dimension:
                try:
                    inferred_dim = DimensionalChecker.infer_dimension(
                        resp.candidate_symbolic,
                        symbol_dimensions=problem.symbol_dimensions,
                    )
                    expected_dim_vec = DimensionalChecker.infer_dimension(
                        step.target_symbolic,
                        symbol_dimensions=problem.symbol_dimensions,
                    )
                    dim_ok = inferred_dim == expected_dim_vec
                except Exception:
                    dim_ok = False

            # 3. Check Numeric Accuracy (if numerical value expected)
            numeric_ok = True
            if step.expected_numeric is not None:
                if resp.candidate_numeric is not None:
                    numeric_ok = bool(np.isclose(resp.candidate_numeric, step.expected_numeric, rtol=step.tolerance))
                else:
                    numeric_ok = False

            # 4. Error classification
            if symbolic_ok and dim_ok and numeric_ok:
                category = "NONE"
            elif not dim_ok:
                category = "DIMENSIONAL_VIOLATION"
            elif not symbolic_ok:
                category = "SYMBOLIC_MISMATCH"
            else:
                category = "ARITHMETIC_ERROR"

            step_evals.append(
                StepEvaluation(
                    step_number=step.step_number,
                    symbolic_correct=symbolic_ok,
                    dimensional_correct=dim_ok,
                    numeric_correct=numeric_ok,
                    error_category=category,
                )
            )

        correct_steps = sum(1 for se in step_evals if se.error_category == "NONE")
        hallucinations = sum(1 for se in step_evals if se.error_category in ("SYMBOLIC_MISMATCH", "DIMENSIONAL_VIOLATION"))
        all_ok = correct_steps == len(problem.steps)

        # Check final step
        final_ok = step_evals[-1].error_category == "NONE" if step_evals else False

        return ProblemEvaluation(
            problem_id=problem.problem_id,
            all_steps_correct=all_ok,
            final_answer_correct=final_ok,
            step_results=step_evals,
            total_steps=len(problem.steps),
            correct_steps_count=correct_steps,
            hallucination_count=hallucinations,
            reasoning_tokens=attempt.total_reasoning_tokens,
        )
