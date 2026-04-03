"""Shared core schemas for DEF-CAI runtime objects."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FindingKind(StrEnum):
    OBSERVATION = "observation"
    WEAKNESS = "weakness"
    VULNERABILITY = "vulnerability"
    MISCONFIGURATION = "misconfiguration"
    EXPLOIT_PATH = "exploit_path"


class MessageRecord(BaseModel):
    role: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentSpec(BaseModel):
    name: str
    instructions: str
    tools: list[str] = Field(default_factory=list)
    model_backend: str = "openai"
    model_name: str | None = None
    handoff_targets: list[str] = Field(default_factory=list)
    hitl_required: bool = False
    tracing_enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("name must not be empty")
        return normalized


class ToolExecutionRecord(BaseModel):
    tool_name: str
    command: str
    args: list[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_seconds: float = 0.0
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    policy_verdict: str = "pending"
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("duration_seconds")
    @classmethod
    def _validate_duration(cls, value: float) -> float:
        if value < 0:
            raise ValueError("duration_seconds must be >= 0")
        return value
