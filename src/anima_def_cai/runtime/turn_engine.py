"""Typed turn engine for CAI-style multi-agent workflows."""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from time import perf_counter

from pydantic import BaseModel, Field

from anima_def_cai.core.agent_registry import build_agent
from anima_def_cai.core.handoffs import transfer
from anima_def_cai.patterns import PatternPlan, PatternStep
from anima_def_cai.schemas import FindingRecord, MessageRecord, TurnState
from anima_def_cai.settings import DEFCAISettings


class ActionKind(StrEnum):
    MESSAGE = "message"
    FINDING = "finding"
    HANDOFF = "handoff"
    STOP = "stop"
    INTERRUPT = "interrupt"


class AgentAction(BaseModel):
    kind: ActionKind
    message: str | None = None
    finding: FindingRecord | None = None
    target_agent: str | None = None
    reason: str | None = None


class RunSummary(BaseModel):
    turns_executed: int
    findings_count: int
    visited_agents: list[str] = Field(default_factory=list)
    handoffs: list[str] = Field(default_factory=list)
    interrupted: bool = False
    duration_seconds: float = 0.0


ActionResolver = Callable[[str, TurnState, PatternStep], AgentAction]


def _default_action(agent_name: str, state: TurnState, step: PatternStep) -> AgentAction:
    return AgentAction(
        kind=ActionKind.MESSAGE,
        message=f"{agent_name} executed step: {step.purpose}",
    )


def _apply_action(
    state: TurnState,
    *,
    action: AgentAction,
    source_agent: str,
    handoffs: list[str],
) -> TurnState:
    updated = state.model_copy(deep=True)
    updated.current_agent = source_agent

    if action.message:
        updated.messages.append(MessageRecord(role="assistant", content=action.message))

    if action.finding:
        updated.findings.append(action.finding)

    if action.kind is ActionKind.HANDOFF:
        target = action.target_agent or ""
        updated = transfer(
            updated, target, source_agent=source_agent, reason=action.reason or "handoff"
        )
        handoffs.append(f"{source_agent}->{target}")
    elif action.kind is ActionKind.INTERRUPT:
        updated.interrupted = True
    elif action.kind is ActionKind.STOP:
        updated.metadata["stop_reason"] = action.reason or "completed"
    return updated


def run_turn(
    state: TurnState,
    pattern: PatternPlan,
    settings: DEFCAISettings,
    action_resolver: ActionResolver | None = None,
) -> RunSummary:
    resolver = action_resolver or _default_action
    working_state = state.model_copy(deep=True)
    visited_agents: list[str] = []
    handoffs: list[str] = []
    started = perf_counter()

    for step in pattern.iter_steps():
        agent = build_agent(step.agent_name, settings)
        working_state.current_agent = agent.name
        visited_agents.append(agent.name)
        action = resolver(agent.name, working_state, step)
        working_state = _apply_action(
            working_state,
            action=action,
            source_agent=agent.name,
            handoffs=handoffs,
        )
        if working_state.interrupted and step.stop_on_interrupt:
            break
        if action.kind is ActionKind.STOP:
            break

    summary = RunSummary(
        turns_executed=len(visited_agents),
        findings_count=len(working_state.findings),
        visited_agents=visited_agents,
        handoffs=handoffs,
        interrupted=working_state.interrupted,
        duration_seconds=perf_counter() - started,
    )
    state.current_agent = working_state.current_agent
    state.messages = working_state.messages
    state.findings = working_state.findings
    state.interrupted = working_state.interrupted
    state.operator_override = working_state.operator_override
    state.metadata = working_state.metadata
    return summary
