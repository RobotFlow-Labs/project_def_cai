"""Pattern abstractions for sequential and parallel execution."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


ExecutionMode = Literal["sequential", "parallel"]


class PatternStep(BaseModel):
    agent_name: str
    purpose: str
    stop_on_interrupt: bool = True
    allow_handoff: bool = True


class PatternPlan(BaseModel):
    name: str
    mode: ExecutionMode = "sequential"
    steps: list[PatternStep] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_steps(self) -> "PatternPlan":
        if not self.steps:
            raise ValueError("PatternPlan requires at least one step")
        return self

    def iter_steps(self) -> list[PatternStep]:
        return list(self.steps)

    def agent_names(self) -> list[str]:
        return [step.agent_name for step in self.steps]
