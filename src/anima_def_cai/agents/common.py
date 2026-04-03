"""Helpers shared by role-specific agent definitions."""

from __future__ import annotations

from anima_def_cai.schemas import AgentSpec
from anima_def_cai.settings import DEFCAISettings


def build_role_agent(
    *,
    name: str,
    instructions: str,
    tools: list[str],
    settings: DEFCAISettings,
    handoff_targets: list[str] | None = None,
    hitl_required: bool = False,
) -> AgentSpec:
    return AgentSpec(
        name=name,
        instructions=instructions.strip(),
        tools=tools,
        model_backend=settings.model_backend,
        model_name=settings.model_name,
        handoff_targets=handoff_targets or [],
        hitl_required=hitl_required,
        tracing_enabled=settings.tracing_enabled,
        metadata={"tool_policy": settings.tool_policy},
    )
