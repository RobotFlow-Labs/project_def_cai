"""Runtime schemas for turns, findings, and tool policy."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

from .base import FindingKind, MessageRecord, Severity


class ToolPolicyVerdict(BaseModel):
    allowed: bool
    policy: str
    reason: str
    matched_rule: str | None = None


class FindingRecord(BaseModel):
    title: str
    summary: str
    severity: Severity = Severity.INFO
    kind: FindingKind = FindingKind.OBSERVATION
    evidence: list[str] = Field(default_factory=list)
    reproduction: str = ""
    confidence: float = 0.5
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("confidence")
    @classmethod
    def _validate_confidence(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        return value


class TurnState(BaseModel):
    objective: str
    messages: list[MessageRecord] = Field(default_factory=list)
    trace_id: str
    current_agent: str | None = None
    findings: list[FindingRecord] = Field(default_factory=list)
    interrupted: bool = False
    operator_override: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("objective", "trace_id")
    @classmethod
    def _validate_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("value must not be empty")
        return normalized

    def append_message(self, role: str, content: str) -> None:
        self.messages.append(MessageRecord(role=role, content=content))

    def add_finding(self, finding: FindingRecord) -> None:
        self.findings.append(finding)
