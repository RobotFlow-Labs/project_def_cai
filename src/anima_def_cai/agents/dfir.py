"""DFIR role definition."""

from __future__ import annotations

from anima_def_cai.agents.common import build_role_agent
from anima_def_cai.schemas import AgentSpec
from anima_def_cai.settings import DEFCAISettings

DFIR_PROMPT = """
You are the DEF-CAI DFIR Agent.
Reconstruct evidence, timeline suspicious activity, preserve forensics integrity,
and explain incident-response implications without overstating certainty.
"""


def build_dfir_agent(settings: DEFCAISettings) -> AgentSpec:
    return build_role_agent(
        name="dfir",
        instructions=DFIR_PROMPT,
        tools=["generic_linux_command", "execute_code", "shodan_search", "web_search"],
        settings=settings,
        handoff_targets=["blue_team", "reporter"],
    )
