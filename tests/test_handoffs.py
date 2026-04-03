import pytest

from anima_def_cai.core.handoffs import allowed_handoffs, transfer
from anima_def_cai.patterns import BUG_BOUNTY_PATTERN
from anima_def_cai.runtime.turn_engine import ActionKind, AgentAction, run_turn
from anima_def_cai.schemas import TurnState
from anima_def_cai.settings import DEFCAISettings


def test_bug_bounty_handoff_targets_include_retester() -> None:
    assert "retester" in allowed_handoffs("bug_bounty")


def test_transfer_updates_current_agent() -> None:
    state = TurnState(objective="verify", trace_id="trace-handoff-1", current_agent="bug_bounty")
    updated = transfer(state, "retester", reason="validate finding")
    assert updated.current_agent == "retester"
    assert "HANDOFF" in updated.messages[-1].content


def test_invalid_handoff_is_rejected() -> None:
    state = TurnState(objective="verify", trace_id="trace-handoff-2", current_agent="retester")
    with pytest.raises(ValueError):
        transfer(state, "blue_team")


def test_run_turn_tracks_handoffs() -> None:
    state = TurnState(objective="disclose", trace_id="trace-handoff-3")

    def resolver(agent_name: str, _state: TurnState, _step) -> AgentAction:
        if agent_name == "bug_bounty":
            return AgentAction(
                kind=ActionKind.HANDOFF,
                message="Need retest",
                target_agent="retester",
                reason="candidate finding",
            )
        return AgentAction(kind=ActionKind.STOP, reason="complete")

    summary = run_turn(state, BUG_BOUNTY_PATTERN, DEFCAISettings(), action_resolver=resolver)
    assert "bug_bounty->retester" in summary.handoffs
