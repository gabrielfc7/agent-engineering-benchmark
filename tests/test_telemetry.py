"""Tests for telemetry metrics, pass@k estimation, and summary aggregation."""

import pytest
import numpy as np
from agent_benchmark.harness import ProblemEvaluation, StepEvaluation
from agent_benchmark.telemetry import (
    BenchmarkReporter,
    calculate_pass_at_k,
    compute_benchmark_summary,
)


def test_pass_at_k_exact_values():
    """Verify pass@k calculation matches theoretical combinatorics."""
    # If 10 samples and all 10 correct, pass@1 = 1.0, pass@5 = 1.0
    assert calculate_pass_at_k(n=10, c=10, k=1) == 1.0
    # If 10 samples and 0 correct, pass@k = 0.0
    assert calculate_pass_at_k(n=10, c=0, k=1) == 0.0
    # If n=2, c=1, k=1 -> 1 - (1/2) = 0.5
    assert np.isclose(calculate_pass_at_k(n=2, c=1, k=1), 0.5)


def test_compute_benchmark_summary_and_reporting():
    """Verify aggregation of problem evaluations and report rendering."""
    evals = [
        ProblemEvaluation(
            problem_id="PROB-1",
            all_steps_correct=True,
            final_answer_correct=True,
            step_results=[
                StepEvaluation(step_number=1, symbolic_correct=True, dimensional_correct=True, numeric_correct=True, error_category="NONE"),
                StepEvaluation(step_number=2, symbolic_correct=True, dimensional_correct=True, numeric_correct=True, error_category="NONE"),
            ],
            total_steps=2,
            correct_steps_count=2,
            hallucination_count=0,
            reasoning_tokens=500,
        ),
        ProblemEvaluation(
            problem_id="PROB-2",
            all_steps_correct=False,
            final_answer_correct=False,
            step_results=[
                StepEvaluation(step_number=1, symbolic_correct=True, dimensional_correct=True, numeric_correct=True, error_category="NONE"),
                StepEvaluation(step_number=2, symbolic_correct=False, dimensional_correct=False, numeric_correct=False, error_category="DIMENSIONAL_VIOLATION"),
            ],
            total_steps=2,
            correct_steps_count=1,
            hallucination_count=1,
            reasoning_tokens=700,
        ),
    ]

    summary = compute_benchmark_summary(evals)

    assert summary.total_problems == 2
    assert summary.problems_solved == 1
    assert summary.problem_solve_rate == 50.0
    assert summary.total_steps == 4
    assert summary.steps_correct == 3
    assert summary.step_accuracy_rate == 75.0
    assert summary.total_hallucinations == 1
    assert summary.total_reasoning_tokens == 1200
    assert summary.avg_tokens_per_problem == 600.0

    md_report = BenchmarkReporter.format_markdown(summary)
    assert "Engineering Agent Benchmark Summary" in md_report
    assert "50.0%" in md_report
