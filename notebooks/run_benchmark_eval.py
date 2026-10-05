"""Benchmark evaluation runner comparing agents across standard engineering problems."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agent_benchmark.harness import (
    AgentProblemAttempt,
    AgentStepResponse,
    BenchmarkEvaluator,
    get_standard_engineering_suite,
)
from agent_benchmark.telemetry import (
    BenchmarkReporter,
    compute_benchmark_summary,
)


def create_mock_agent_attempts() -> dict[str, list[AgentProblemAttempt]]:
    """Create simulated agent traces to demonstrate verification accuracy and error localization."""
    # Agent 1: Advanced Symbolic Agent (Gemini Flash style: correct math, varied syntaxes)
    agent_flash_attempts = [
        # ENG-STR-01: Beam deflection (uses factored syntax)
        AgentProblemAttempt(
            problem_id="ENG-STR-01",
            agent_id="Gemini-Flash-Engineering",
            total_reasoning_tokens=520,
            step_responses=[
                AgentStepResponse(step_number=1, candidate_symbolic="P * L", candidate_numeric=5000.0),
                AgentStepResponse(step_number=2, candidate_symbolic="(P * L * c) / I"),
                AgentStepResponse(step_number=3, candidate_symbolic="(1/3) * (P / E) * (L**3 / I)", candidate_numeric=0.0125),
            ],
        ),
        # ENG-FLD-02: Reynolds Number
        AgentProblemAttempt(
            problem_id="ENG-FLD-02",
            agent_id="Gemini-Flash-Engineering",
            total_reasoning_tokens=480,
            step_responses=[
                AgentStepResponse(step_number=1, candidate_symbolic="(4 * Q) / (pi * D**2)"),
                AgentStepResponse(step_number=2, candidate_symbolic="(rho * v * D) / mu"),
                AgentStepResponse(step_number=3, candidate_symbolic="64 / Re", candidate_numeric=0.04),
            ],
        ),
        # ENG-THM-03: Gibbs Free Energy
        AgentProblemAttempt(
            problem_id="ENG-THM-03",
            agent_id="Gemini-Flash-Engineering",
            total_reasoning_tokens=410,
            step_responses=[
                AgentStepResponse(step_number=1, candidate_symbolic="dH - T * dS"),
                AgentStepResponse(step_number=2, candidate_symbolic="exp(-dG / (R * T))", candidate_numeric=1.45),
            ],
        ),
        # ENG-ELE-04: RLC Resonant Frequency
        AgentProblemAttempt(
            problem_id="ENG-ELE-04",
            agent_id="Gemini-Flash-Engineering",
            total_reasoning_tokens=430,
            step_responses=[
                AgentStepResponse(step_number=1, candidate_symbolic="(L * C)**(-1/2)"),
                AgentStepResponse(step_number=2, candidate_symbolic="(1 / R) * sqrt(L / C)", candidate_numeric=10.0),
            ],
        ),
        # ENG-CTRL-05: Harmonic Oscillator
        AgentProblemAttempt(
            problem_id="ENG-CTRL-05",
            agent_id="Gemini-Flash-Engineering",
            total_reasoning_tokens=390,
            step_responses=[
                AgentStepResponse(step_number=1, candidate_symbolic="omega_n * sqrt(1 - zeta**2)"),
                AgentStepResponse(step_number=2, candidate_symbolic="(2 * pi * zeta) / sqrt(1 - zeta**2)", candidate_numeric=0.64),
            ],
        ),
    ]

    # Agent 2: Baseline Agent (Makes typical LLM errors: dimensional slip, arithmetic mistake)
    agent_baseline_attempts = [
        # ENG-STR-01: Beam deflection (arithmetic error in step 1)
        AgentProblemAttempt(
            problem_id="ENG-STR-01",
            agent_id="Baseline-LLM",
            total_reasoning_tokens=850,
            step_responses=[
                AgentStepResponse(step_number=1, candidate_symbolic="P * L", candidate_numeric=4200.0),  # Wrong numeric
                AgentStepResponse(step_number=2, candidate_symbolic="(P * L * c) / I"),
                AgentStepResponse(step_number=3, candidate_symbolic="(P * L**3) / (3 * E * I)", candidate_numeric=0.0125),
            ],
        ),
        # ENG-FLD-02: Reynolds number (valid)
        AgentProblemAttempt(
            problem_id="ENG-FLD-02",
            agent_id="Baseline-LLM",
            total_reasoning_tokens=790,
            step_responses=[
                AgentStepResponse(step_number=1, candidate_symbolic="(4 * Q) / (pi * D**2)"),
                AgentStepResponse(step_number=2, candidate_symbolic="(rho * v * D) / mu"),
                AgentStepResponse(step_number=3, candidate_symbolic="64 / Re", candidate_numeric=0.04),
            ],
        ),
        # ENG-THM-03: Gibbs (dimensional hallucination: forgets temperature scaling T*dS -> dH - dS)
        AgentProblemAttempt(
            problem_id="ENG-THM-03",
            agent_id="Baseline-LLM",
            total_reasoning_tokens=650,
            step_responses=[
                AgentStepResponse(step_number=1, candidate_symbolic="dH - dS"),  # Energy - HeatCapacity -> Dimension mismatch!
                AgentStepResponse(step_number=2, candidate_symbolic="exp(-dG / (R * T))"),
            ],
        ),
        # ENG-ELE-04: RLC (symbolic mistake in Q-factor)
        AgentProblemAttempt(
            problem_id="ENG-ELE-04",
            agent_id="Baseline-LLM",
            total_reasoning_tokens=710,
            step_responses=[
                AgentStepResponse(step_number=1, candidate_symbolic="1 / sqrt(L * C)"),
                AgentStepResponse(step_number=2, candidate_symbolic="R / sqrt(L / C)"),  # Inverted Q-factor
            ],
        ),
        # ENG-CTRL-05: Harmonic (valid)
        AgentProblemAttempt(
            problem_id="ENG-CTRL-05",
            agent_id="Baseline-LLM",
            total_reasoning_tokens=620,
            step_responses=[
                AgentStepResponse(step_number=1, candidate_symbolic="omega_n * sqrt(1 - zeta**2)"),
                AgentStepResponse(step_number=2, candidate_symbolic="(2 * pi * zeta) / sqrt(1 - zeta**2)", candidate_numeric=0.64),
            ],
        ),
    ]

    return {
        "Gemini-Flash-Engineering": agent_flash_attempts,
        "Baseline-LLM": agent_baseline_attempts,
    }


def main():
    print("=" * 75)
    print("AUTONOMOUS AGENT BENCHMARK HARNESS FOR ENGINEERING SYSTEMS")
    print("=" * 75)

    suite = get_standard_engineering_suite()
    print(f"Loaded benchmark suite with {len(suite)} multi-step engineering tasks across:")
    for prob in suite:
        print(f"  • [{prob.problem_id}] {prob.title} ({prob.domain}) - {len(prob.steps)} milestone steps")

    agents_data = create_mock_agent_attempts()

    for agent_name, attempts in agents_data.items():
        print(f"\n{'-' * 75}")
        print(f"EVALUATING AGENT: {agent_name}")
        print(f"{'-' * 75}")

        prob_map = {p.problem_id: p for p in suite}
        evaluations = []

        # Compare exact string match vs symbolic verification
        string_matches = 0
        total_steps = 0

        for att in attempts:
            prob = prob_map[att.problem_id]
            res = BenchmarkEvaluator.evaluate_attempt(prob, att)
            evaluations.append(res)

            # Check string match
            for s_idx, s in enumerate(prob.steps):
                total_steps += 1
                if s_idx < len(att.step_responses) and att.step_responses[s_idx].candidate_symbolic:
                    if att.step_responses[s_idx].candidate_symbolic == s.target_symbolic:
                        string_matches += 1

        summary = compute_benchmark_summary(evaluations)

        print(f"  Raw String Exact Match Accuracy : {(string_matches / total_steps) * 100:.1f}%")
        print(f"  Symbolic Verification Accuracy   : {summary.step_accuracy_rate:.1f}%")
        print(f"  Overall Problem Pass Rate        : {summary.problem_solve_rate:.1f}% ({summary.problems_solved}/{summary.total_problems})")
        print(f"  Step Hallucination Rate          : {summary.step_hallucination_rate:.1f}% ({summary.total_hallucinations} errors)")
        print(f"  Average Reasoning Tokens/Task    : {summary.avg_tokens_per_problem:,.0f} tokens")
        print(f"  Compute Efficiency (Tokens/Step) : {summary.tokens_per_correct_step:,.0f} tokens/step")

        print("\n  Error Breakdown:")
        for err_type, count in summary.error_distribution.items():
            if count > 0:
                print(f"    • {err_type}: {count}")

    print("\n" + "=" * 75)
    print("BENCHMARK EVALUATION COMPLETE")
    print("=" * 75)


if __name__ == "__main__":
    main()
