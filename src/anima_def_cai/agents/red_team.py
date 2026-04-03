"""Red team role definition."""

from __future__ import annotations

from anima_def_cai.agents.common import build_role_agent
from anima_def_cai.schemas import AgentSpec
from anima_def_cai.settings import DEFCAISettings

RED_TEAM_PROMPT = """
You are the DEF-CAI Red Team Agent.
Work like a disciplined offensive security operator in a controlled lab.
Prioritize recon, exploit-path enumeration, and concise evidence capture.
Escalate to the blue team or DFIR flow when the workflow requires validation,
containment guidance, or cross-checking an observed weakness.
"""


def build_red_team_agent(settings: DEFCAISettings) -> AgentSpec:
    return build_role_agent(
        name="red_team",
        instructions=RED_TEAM_PROMPT,
        tools=["generic_linux_command", "execute_code", "web_search"],
        settings=settings,
        handoff_targets=["blue_team", "dfir", "reporter"],
    )
