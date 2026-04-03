"""Agent factory and registry for the DEF-CAI runtime."""

from __future__ import annotations

from collections.abc import Callable

from anima_def_cai.agents import (
    build_blue_team_agent,
    build_bug_bounty_agent,
    build_dfir_agent,
    build_red_team_agent,
    build_reporter_agent,
    build_retester_agent,
)
from anima_def_cai.schemas import AgentSpec
from anima_def_cai.settings import DEFCAISettings

AgentFactory = Callable[[DEFCAISettings], AgentSpec]

_REGISTRY: dict[str, AgentFactory] = {
    "red_team": build_red_team_agent,
    "bug_bounty": build_bug_bounty_agent,
    "blue_team": build_blue_team_agent,
    "dfir": build_dfir_agent,
    "retester": build_retester_agent,
    "reporter": build_reporter_agent,
}


def list_agents() -> list[str]:
    return sorted(_REGISTRY)


def has_agent(name: str) -> bool:
    return name in _REGISTRY


def build_agent(name: str, settings: DEFCAISettings) -> AgentSpec:
    try:
        factory = _REGISTRY[name]
    except KeyError as exc:
        available = ", ".join(list_agents())
        raise ValueError(f"Unknown agent '{name}'. Available agents: {available}") from exc
    return factory(settings)
