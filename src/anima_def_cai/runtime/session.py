"""Session lifecycle management and operator interrupts."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from anima_def_cai.patterns import BUG_BOUNTY_PATTERN, RED_BLUE_SEQUENTIAL_PATTERN, PatternPlan
from anima_def_cai.runtime.artifacts import write_artifacts
from anima_def_cai.runtime.turn_engine import RunSummary, run_turn
from anima_def_cai.schemas import MessageRecord, TurnState
from anima_def_cai.settings import DEFCAISettings


class SessionRequest(BaseModel):
    objective: str
    agent_name: str | None = None
    pattern_name: str | None = None
    output_root: Path | None = None


class SessionResult(BaseModel):
    state: TurnState
    summary: RunSummary
    artifact_dir: Path


def _single_agent_pattern(agent_name: str) -> PatternPlan:
    return PatternPlan(
        name=f"{agent_name}_single",
        steps=[{"agent_name": agent_name, "purpose": f"execute {agent_name} objective"}],
    )


def resolve_pattern(request: SessionRequest) -> PatternPlan:
    if request.pattern_name == "bug_bounty":
        return BUG_BOUNTY_PATTERN
    if request.pattern_name == "red_blue":
        return RED_BLUE_SEQUENTIAL_PATTERN
    if request.agent_name:
        return _single_agent_pattern(request.agent_name)
    return RED_BLUE_SEQUENTIAL_PATTERN


def pause_and_collect(state: TurnState, operator_input: str = "") -> TurnState:
    updated = state.model_copy(deep=True)
    updated.interrupted = False
    updated.operator_override = bool(operator_input)
    if operator_input:
        updated.messages.append(MessageRecord(role="operator", content=operator_input))
    return updated


def run_session(request: SessionRequest, settings: DEFCAISettings) -> SessionResult:
    state = TurnState(objective=request.objective, trace_id="trace-session-001")
    pattern = resolve_pattern(request)
    summary = run_turn(state, pattern, settings)
    artifact_dir = write_artifacts(
        state.trace_id,
        state.findings,
        root=request.output_root or settings.artifact_root,
    )
    return SessionResult(state=state, summary=summary, artifact_dir=artifact_dir)
