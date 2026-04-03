"""OSINT adapters with explicit network gating."""

from __future__ import annotations

import os

from .common import ToolObservation


def web_search(query: str) -> ToolObservation:
    if os.getenv("DEF_CAI_ENABLE_NETWORK", "false").lower() != "true":
        return ToolObservation(
            tool_name="web_search",
            command=query,
            stdout="Network-disabled stub result",
            metadata={"stub": True},
        )
    return ToolObservation(
        tool_name="web_search", command=query, stdout="Live search not yet wired"
    )


def shodan_lookup(target: str) -> ToolObservation:
    api_key = os.getenv("SHODAN_API_KEY")
    if not api_key:
        return ToolObservation(
            tool_name="shodan_lookup",
            command=target,
            stderr="SHODAN_API_KEY is not configured",
            exit_code=2,
            allowed=False,
        )
    return ToolObservation(tool_name="shodan_lookup", command=target, stdout="Shodan lookup stub")
