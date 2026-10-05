"""Tests for benchmark evaluator and step error localization."""

import pytest
from agent_benchmark.harness import (
    AgentProblemAttempt,
    AgentStepResponse,
    BenchmarkEvaluator,
    get_standard_engineering_suite,
)


def test_evaluator_perfect_attempt():
    """Verify evaluator scores a 100% correct multi-step agent attempt."""
    suite = get_standard_engineering_suite()
    beam_prob = suite[0]  # ENG-STR-01

    attempt = AgentProblemAttempt(
        problem_id="ENG-STR-01",
        total_reasoning_tokens=450,
        step_responses=[
            AgentStepResponse(step_number=1, candidate_symbolic="P * L", candidate_numeric=5000.0),
            AgentStepResponse(step_number=2, candidate_symbolic="(P * L * c) / I"),
            AgentStepResponse(step_number=3, candidate_symbolic="(P * L**3) / (3 * E * I)", candidate_numeric=0.0125),
        ],
    )

    eval_result = BenchmarkEvaluator.evaluate_attempt(beam_prob, attempt)

    assert eval_result.all_steps_correct is True
    assert eval_result.final_answer_correct is True
    assert eval_result.hallucination_count == 0
    assert eval_result.correct_steps_count == 3
    for s in eval_result.step_results:
        assert s.error_category == "NONE"


def test_evaluator_detects_errors():
    """Verify evaluator catches symbolic mismatch and arithmetic errors."""
    suite = get_standard_engineering_suite()
    beam_prob = suite[0]

    flawed_attempt = AgentProblemAttempt(
        problem_id="ENG-STR-01",
        total_reasoning_tokens=600,
        step_responses=[
            # Step 1: correct formula, wrong numeric calculation (arithmetic error)
            AgentStepResponse(step_number=1, candidate_symbolic="P * L", candidate_numeric=9999.0),
            # Step 2: wrong symbolic formula
            AgentStepResponse(step_number=2, candidate_symbolic="(P * L) / (c * I)"),
            # Step 3: missing response
        ],
    )

    eval_result = BenchmarkEvaluator.evaluate_attempt(beam_prob, flawed_attempt)

    assert eval_result.all_steps_correct is False
    assert eval_result.step_results[0].error_category == "ARITHMETIC_ERROR"
    assert eval_result.step_results[1].error_category in ("SYMBOLIC_MISMATCH", "DIMENSIONAL_VIOLATION")
    assert eval_result.step_results[2].error_category == "MISSING_RESPONSE"
