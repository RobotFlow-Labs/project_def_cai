"""Retester role definition."""

from __future__ import annotations

from anima_def_cai.agents.common import build_role_agent
from anima_def_cai.schemas import AgentSpec
from anima_def_cai.settings import DEFCAISettings

RETESTER_PROMPT = """
You are the DEF-CAI Retester Agent.
Verify reproducibility, reduce false positives, and tighten reproduction steps.
If a finding is confirmed, prepare it for structured reporting.
"""


def build_retester_agent(settings: DEFCAISettings) -> AgentSpec:
    return build_role_agent(
        name="retester",
        instructions=RETESTER_PROMPT,
        tools=["generic_linux_command", "execute_code"],
        settings=settings,
        handoff_targets=["reporter"],
        hitl_required=True,
    )
