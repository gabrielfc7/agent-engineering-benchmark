"""Benchmark telemetry metrics, pass@k estimation, and error distribution statistics."""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Sequence

from agent_benchmark.harness.evaluator import ProblemEvaluation


def calculate_pass_at_k(n: int, c: int, k: int) -> float:
    """Calculate unbiased pass@k metric (Chen et al., HumanEval).

    Parameters
    ----------
    n : int
        Total number of sampled attempts per task.
    c : int
        Number of correct attempts (c <= n).
    k : int
        Evaluation threshold (k <= n).
    """
    if n - c < k:
        return 1.0
    if n < k or c == 0:
        return 0.0
    return 1.0 - (comb(n - c, k) / comb(n, k))


@dataclass
class BenchmarkSummary:
    """Consolidated benchmark evaluation summary."""

    total_problems: int
    total_steps: int
    problems_solved: int
    problem_solve_rate: float
    steps_correct: int
    step_accuracy_rate: float
    total_hallucinations: int
    step_hallucination_rate: float
    total_reasoning_tokens: int
    avg_tokens_per_problem: float
    tokens_per_correct_step: float
    error_distribution: dict[str, int]


def compute_benchmark_summary(evaluations: Sequence[ProblemEvaluation]) -> BenchmarkSummary:
    """Aggregate step-level evaluations into overall benchmark metrics."""
    total_probs = len(evaluations)
    if total_probs == 0:
        raise ValueError("Cannot summarize empty evaluation list.")

    probs_solved = sum(1 for e in evaluations if e.final_answer_correct)
    total_steps = sum(e.total_steps for e in evaluations)
    steps_correct = sum(e.correct_steps_count for e in evaluations)
    hallucinations = sum(e.hallucination_count for e in evaluations)
    tokens = sum(e.reasoning_tokens for e in evaluations)

    error_dist: dict[str, int] = {
        "SYMBOLIC_MISMATCH": 0,
        "DIMENSIONAL_VIOLATION": 0,
        "ARITHMETIC_ERROR": 0,
        "MISSING_RESPONSE": 0,
    }
    for e in evaluations:
        for s in e.step_results:
            if s.error_category != "NONE":
                error_dist[s.error_category] = error_dist.get(s.error_category, 0) + 1

    return BenchmarkSummary(
        total_problems=total_probs,
        total_steps=total_steps,
        problems_solved=probs_solved,
        problem_solve_rate=(probs_solved / total_probs) * 100.0,
        steps_correct=steps_correct,
        step_accuracy_rate=(steps_correct / total_steps) * 100.0 if total_steps > 0 else 0.0,
        total_hallucinations=hallucinations,
        step_hallucination_rate=(hallucinations / total_steps) * 100.0 if total_steps > 0 else 0.0,
        total_reasoning_tokens=tokens,
        avg_tokens_per_problem=tokens / total_probs,
        tokens_per_correct_step=(tokens / steps_correct) if steps_correct > 0 else float("inf"),
        error_distribution=error_dist,
    )
