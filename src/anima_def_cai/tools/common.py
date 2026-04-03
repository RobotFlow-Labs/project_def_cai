"""Common tool observation models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ToolObservation(BaseModel):
    tool_name: str
    command: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    allowed: bool = True
    artifact_paths: list[Path] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
