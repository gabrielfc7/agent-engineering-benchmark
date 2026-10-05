"""Pydantic data schemas for engineering problem definitions and agent attempts."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class EngineeringStep(BaseModel):
    """A distinct milestone step in a multi-step engineering derivation."""

    step_number: int
    description: str
    target_symbolic: str
    expected_dimension: str | None = None
    expected_numeric: float | None = None
    tolerance: float = 1e-4


class EngineeringProblem(BaseModel):
    """Complete engineering problem definition with ground-truth milestones."""

    problem_id: str
    title: str
    domain: str  # 'Structural', 'Fluids', 'Thermodynamics', 'Electrical', 'Controls'
    problem_statement: str
    parameters: dict[str, str] = Field(default_factory=dict)
    symbol_dimensions: dict[str, str] = Field(default_factory=dict)
    steps: list[EngineeringStep]
    final_symbolic: str
    final_numeric: float | None = None


class AgentStepResponse(BaseModel):
    """Single step response produced by an AI agent."""

    step_number: int
    candidate_symbolic: str | None = None
    candidate_numeric: float | None = None
    reasoning_tokens: int = 0


class AgentProblemAttempt(BaseModel):
    """Complete attempt by an AI agent on an engineering problem."""

    problem_id: str
    agent_id: str = "agent-candidate"
    total_reasoning_tokens: int = 0
    step_responses: list[AgentStepResponse] = Field(default_factory=list)
