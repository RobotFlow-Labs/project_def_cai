"""Bug bounty workflow preset."""

from __future__ import annotations

from .base import PatternPlan, PatternStep

BUG_BOUNTY_PATTERN = PatternPlan(
    name="bug_bounty_pipeline",
    mode="sequential",
    steps=[
        PatternStep(agent_name="bug_bounty", purpose="discover externally reachable weaknesses"),
        PatternStep(
            agent_name="retester", purpose="verify exploitability and reduce false positives"
        ),
        PatternStep(agent_name="reporter", purpose="prepare a disclosure-ready finding summary"),
    ],
)
