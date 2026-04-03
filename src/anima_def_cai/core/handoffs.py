"""Handoff rules between specialized CAI roles."""

from __future__ import annotations

from pydantic import BaseModel

from anima_def_cai.schemas import MessageRecord, TurnState


class HandoffRule(BaseModel):
    source_agent: str
    target_agent: str
    reason: str


_HANDOFF_MATRIX: dict[str, set[str]] = {
    "bug_bounty": {"retester", "reporter"},
    "retester": {"reporter"},
    "red_team": {"blue_team", "dfir", "reporter"},
    "blue_team": {"dfir", "reporter"},
    "dfir": {"blue_team", "reporter"},
}


def allowed_handoffs(source_agent: str) -> set[str]:
    return set(_HANDOFF_MATRIX.get(source_agent, set()))


def can_handoff(source_agent: str, target_agent: str) -> bool:
    return target_agent in allowed_handoffs(source_agent)


def transfer(
    state: TurnState,
    target_agent: str,
    *,
    source_agent: str | None = None,
    reason: str = "workflow handoff",
) -> TurnState:
    active_source = source_agent or state.current_agent
    if active_source is None:
        raise ValueError("Cannot transfer without a source agent")
    if not can_handoff(active_source, target_agent):
        raise ValueError(f"Handoff from {active_source} to {target_agent} is not allowed")

    updated = state.model_copy(deep=True)
    updated.current_agent = target_agent
    updated.messages.append(
        MessageRecord(
            role="system",
            content=f"HANDOFF: {active_source} -> {target_agent} ({reason})",
        )
    )
    updated.metadata["last_handoff"] = HandoffRule(
        source_agent=active_source,
        target_agent=target_agent,
        reason=reason,
    ).model_dump()
    return updated
