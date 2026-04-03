"""Reporter role definition."""

from __future__ import annotations

from anima_def_cai.agents.common import build_role_agent
from anima_def_cai.schemas import AgentSpec
from anima_def_cai.settings import DEFCAISettings

REPORTER_PROMPT = """
You are the DEF-CAI Reporter Agent.
Convert validated evidence into concise findings, reproduction steps, and severity notes
that a human operator can review or disclose.
"""


def build_reporter_agent(settings: DEFCAISettings) -> AgentSpec:
    return build_role_agent(
        name="reporter",
        instructions=REPORTER_PROMPT,
        tools=["report_markdown"],
        settings=settings,
        handoff_targets=[],
        hitl_required=True,
    )
