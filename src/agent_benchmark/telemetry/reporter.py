"""Benchmark reporting, Markdown/JSON export, and CLI runner."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from agent_benchmark.telemetry.metrics import BenchmarkSummary


class BenchmarkReporter:
    """Formats and exports benchmark evaluations for publication and CI telemetry."""

    @classmethod
    def format_markdown(cls, summary: BenchmarkSummary) -> str:
        """Render publication-grade markdown benchmark report."""
        lines = [
            "# Engineering Agent Benchmark Summary",
            "",
            "| Metric | Result | Benchmark Definition |",
            "|---|---|---|",
            f"| **Overall Problem Pass Rate** | **{summary.problem_solve_rate:.1f}%** ({summary.problems_solved}/{summary.total_problems}) | Multi-step end-to-end task completion |",
            f"| **Step-Level Accuracy** | **{summary.step_accuracy_rate:.1f}%** ({summary.steps_correct}/{summary.total_steps}) | Milestones with valid symbolic & dimensional proof |",
            f"| **Step Hallucination Rate** | **{summary.step_hallucination_rate:.1f}%** ({summary.total_hallucinations}/{summary.total_steps}) | Steps violating algebra or dimensional homogeneity |",
            f"| **Mean Tokens / Problem** | **{summary.avg_tokens_per_problem:,.0f}** | Total chain-of-thought token expenditure |",
            f"| **Tokens per Correct Step** | **{summary.tokens_per_correct_step:,.0f}** | Reasoning compute efficiency |",
            "",
            "### Step Error Categorization",
            "",
            "| Error Category | Frequency | Description |",
            "|---|---|---|",
        ]

        descriptions = {
            "SYMBOLIC_MISMATCH": "Algebraic or mathematical expression does not match ground truth",
            "DIMENSIONAL_VIOLATION": "Expression violates physical dimensional homogeneity",
            "ARITHMETIC_ERROR": "Symbolic formula correct but numerical evaluation is outside tolerance",
            "MISSING_RESPONSE": "Agent skipped or failed to extract milestone milestone",
        }

        for cat, count in summary.error_distribution.items():
            desc = descriptions.get(cat, "")
            lines.append(f"| `{cat}` | {count} | {desc} |")

        return "\n".join(lines)

    @classmethod
    def export_json(cls, summary: BenchmarkSummary, output_path: str | Path) -> None:
        """Export benchmark summary to JSON file."""
        data = {
            "total_problems": summary.total_problems,
            "total_steps": summary.total_steps,
            "problems_solved": summary.problems_solved,
            "problem_solve_rate_pct": summary.problem_solve_rate,
            "steps_correct": summary.steps_correct,
            "step_accuracy_rate_pct": summary.step_accuracy_rate,
            "total_hallucinations": summary.total_hallucinations,
            "step_hallucination_rate_pct": summary.step_hallucination_rate,
            "total_reasoning_tokens": summary.total_reasoning_tokens,
            "avg_tokens_per_problem": summary.avg_tokens_per_problem,
            "tokens_per_correct_step": summary.tokens_per_correct_step,
            "error_distribution": summary.error_distribution,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


def cli_main():
    """Command-line runner entrypoint."""
    print("Agent Engineering Benchmark Harness v0.1.0")
    print("Use `python notebooks/run_benchmark_eval.py` to evaluate agent traces.")
