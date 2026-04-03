"""Trace collection for CAI session actions and decisions.

Records turns, tool invocations, costs, and interruptions for
post-session analysis and evidence retention.

Paper reference: Figure 3, Section 2 — tracing and agent observation.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class TraceEvent(BaseModel):
    """A single trace event within a session."""

    event_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str  # turn, tool_call, handoff, finding, interrupt, cost
    agent: str = ""
    tool: str = ""
    duration_seconds: float = 0.0
    tokens_used: int = 0
    usd_cost: float = 0.0
    verdict: str = ""
    detail: dict[str, Any] = Field(default_factory=dict)


class TraceBundle(BaseModel):
    """Complete session trace with timeline and cost summary."""

    session_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    events: list[TraceEvent] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def total_cost(self) -> float:
        return sum(e.usd_cost for e in self.events)

    @property
    def total_duration(self) -> float:
        return sum(e.duration_seconds for e in self.events)

    @property
    def event_count(self) -> int:
        return len(self.events)


class Tracer:
    """Stateful trace collector for a single session."""

    def __init__(self, session_id: str | None = None) -> None:
        self._bundle = TraceBundle(session_id=session_id or uuid.uuid4().hex[:12])

    @property
    def bundle(self) -> TraceBundle:
        return self._bundle

    def record(
        self,
        event_type: str,
        *,
        agent: str = "",
        tool: str = "",
        duration_seconds: float = 0.0,
        tokens_used: int = 0,
        usd_cost: float = 0.0,
        verdict: str = "",
        detail: dict[str, Any] | None = None,
    ) -> TraceEvent:
        event = TraceEvent(
            event_type=event_type,
            agent=agent,
            tool=tool,
            duration_seconds=duration_seconds,
            tokens_used=tokens_used,
            usd_cost=usd_cost,
            verdict=verdict,
            detail=detail or {},
        )
        self._bundle.events.append(event)
        return event

    def save(self, output_dir: Path) -> Path:
        """Persist the trace bundle to disk as JSON."""
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"trace_{self._bundle.session_id}.json"
        path.write_text(
            json.dumps(self._bundle.model_dump(mode="json"), indent=2, default=str),
            encoding="utf-8",
        )
        return path
