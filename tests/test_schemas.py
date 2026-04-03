from datetime import datetime, timezone

import pytest

from anima_def_cai.schemas import (
    AgentSpec,
    FindingKind,
    FindingRecord,
    MessageRecord,
    Severity,
    ToolExecutionRecord,
    ToolPolicyVerdict,
    TurnState,
)


def test_agent_spec_requires_name() -> None:
    with pytest.raises(ValueError):
        AgentSpec(name="   ", instructions="test")


def test_turn_state_accepts_messages_and_findings() -> None:
    state = TurnState(objective="audit host", trace_id="trace-1")
    state.append_message(role="user", content="scan the box")
    state.add_finding(
        FindingRecord(
            title="Open SSH",
            summary="Port 22 is reachable",
            severity=Severity.LOW,
            kind=FindingKind.OBSERVATION,
            confidence=0.8,
        )
    )
    assert len(state.messages) == 1
    assert state.findings[0].title == "Open SSH"


def test_confidence_bounds_are_enforced() -> None:
    with pytest.raises(ValueError):
        FindingRecord(
            title="Invalid",
            summary="bad",
            confidence=1.5,
        )


def test_tool_execution_rejects_negative_duration() -> None:
    with pytest.raises(ValueError):
        ToolExecutionRecord(
            tool_name="generic_linux_command",
            command="ls",
            duration_seconds=-1,
        )


def test_schema_models_round_trip() -> None:
    message = MessageRecord(
        role="assistant",
        content="done",
        created_at=datetime.now(timezone.utc),
    )
    verdict = ToolPolicyVerdict(allowed=True, policy="restricted", reason="allowlisted")
    state = TurnState(
        objective="collect evidence",
        trace_id="trace-2",
        messages=[message],
        metadata={"policy": verdict.model_dump()},
    )
    assert state.messages[0].role == "assistant"
    assert state.metadata["policy"]["allowed"] is True
