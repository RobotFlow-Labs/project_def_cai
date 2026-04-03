import pytest

from anima_def_cai.patterns import (
    BUG_BOUNTY_PATTERN,
    PatternPlan,
    PatternStep,
    RED_BLUE_PARALLEL_PATTERN,
)
from anima_def_cai.runtime.turn_engine import ActionKind, AgentAction, run_turn
from anima_def_cai.schemas import FindingRecord, TurnState
from anima_def_cai.settings import DEFCAISettings


def test_pattern_plan_requires_steps() -> None:
    with pytest.raises(ValueError):
        PatternPlan(name="empty", steps=[])


def test_pattern_presets_expose_expected_agents() -> None:
    assert BUG_BOUNTY_PATTERN.agent_names() == ["bug_bounty", "retester", "reporter"]
    assert RED_BLUE_PARALLEL_PATTERN.mode == "parallel"


def test_run_turn_collects_findings() -> None:
    state = TurnState(objective="find issues", trace_id="trace-pattern-1")
    plan = PatternPlan(
        name="single",
        steps=[PatternStep(agent_name="red_team", purpose="discover issues")],
    )

    def resolver(agent_name: str, _state: TurnState, _step: PatternStep) -> AgentAction:
        return AgentAction(
            kind=ActionKind.FINDING,
            message=f"{agent_name} found something",
            finding=FindingRecord(title="Issue", summary="Found"),
        )

    summary = run_turn(state, plan, DEFCAISettings(), action_resolver=resolver)
    assert summary.turns_executed == 1
    assert summary.findings_count == 1
    assert state.findings[0].title == "Issue"
