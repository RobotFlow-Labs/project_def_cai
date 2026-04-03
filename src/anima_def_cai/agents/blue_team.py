"""Blue team role definition."""

from __future__ import annotations

from anima_def_cai.agents.common import build_role_agent
from anima_def_cai.schemas import AgentSpec
from anima_def_cai.settings import DEFCAISettings

BLUE_TEAM_PROMPT = """
You are the DEF-CAI Blue Team Agent.
Analyze detections, mitigations, containment actions, and defensive follow-ups.
Preserve evidence, prefer low-risk recommendations, and summarize hardening steps
that can be validated by operators.
"""


def build_blue_team_agent(settings: DEFCAISettings) -> AgentSpec:
    return build_role_agent(
        name="blue_team",
        instructions=BLUE_TEAM_PROMPT,
        tools=["generic_linux_command", "execute_code", "web_search"],
        settings=settings,
        handoff_targets=["dfir", "reporter"],
    )
