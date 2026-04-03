"""Preset patterns aligned with the paper's red/blue roles."""

from __future__ import annotations

from .base import PatternPlan, PatternStep

RED_BLUE_SEQUENTIAL_PATTERN = PatternPlan(
    name="red_blue_sequential",
    mode="sequential",
    steps=[
        PatternStep(agent_name="red_team", purpose="enumerate and validate offensive paths"),
        PatternStep(agent_name="blue_team", purpose="translate findings into defensive action"),
    ],
)

RED_BLUE_PARALLEL_PATTERN = PatternPlan(
    name="red_blue_parallel",
    mode="parallel",
    steps=[
        PatternStep(agent_name="red_team", purpose="explore offensive posture"),
        PatternStep(agent_name="blue_team", purpose="mirror defensive analysis"),
    ],
)
