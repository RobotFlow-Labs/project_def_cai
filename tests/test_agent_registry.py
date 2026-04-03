import pytest

from anima_def_cai.core.agent_registry import build_agent, list_agents
from anima_def_cai.settings import DEFCAISettings


def test_agent_registry_contains_required_roles() -> None:
    names = list_agents()
    for expected in ("red_team", "bug_bounty", "blue_team", "dfir", "retester"):
        assert expected in names


def test_build_agent_returns_typed_spec() -> None:
    settings = DEFCAISettings()
    agent = build_agent("bug_bounty", settings)
    assert agent.name == "bug_bounty"
    assert "retester" in agent.handoff_targets
    assert agent.model_backend == settings.model_backend


def test_unknown_agent_raises() -> None:
    with pytest.raises(ValueError):
        build_agent("ghost", DEFCAISettings())
