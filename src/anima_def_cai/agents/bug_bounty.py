"""Bug bounty role definition."""

from __future__ import annotations

from anima_def_cai.agents.common import build_role_agent
from anima_def_cai.schemas import AgentSpec
from anima_def_cai.settings import DEFCAISettings

BUG_BOUNTY_PROMPT = """
You are the DEF-CAI Bug Bounty Agent.
Focus on externally reachable attack surface, reproducible findings, severity framing,
and responsible-disclosure quality notes. Handoff to retester for verification and to
reporter when a finding is ready for a human-readable write-up.
"""


def build_bug_bounty_agent(settings: DEFCAISettings) -> AgentSpec:
    return build_role_agent(
        name="bug_bounty",
        instructions=BUG_BOUNTY_PROMPT,
        tools=["generic_linux_command", "execute_code", "shodan_search", "google_search"],
        settings=settings,
        handoff_targets=["retester", "reporter"],
        hitl_required=True,
    )
