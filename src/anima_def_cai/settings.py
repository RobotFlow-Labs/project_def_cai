"""Typed DEF-CAI settings and config loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal
import tomllib

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ModelBackend = Literal[
    "openai",
    "anthropic",
    "google",
    "deepseek",
    "alias",
    "ollama",
    "mock",
]
ToolPolicy = Literal["audit", "restricted", "lab", "off"]
ComputeBackend = Literal["auto", "mlx", "cuda", "cpu"]


class DEFCAISettings(BaseSettings):
    """Runtime settings shared across CLI, tests, and later API surfaces."""

    model_config = SettingsConfigDict(
        env_prefix="DEF_CAI_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    module_name: str = "def-cai"
    codename: str = "DEF-CAI"
    paper_arxiv: str = "2504.06017"
    python_version: str = "3.11"

    model_backend: ModelBackend = "openai"
    model_name: str = "gpt-4o-2024-11-20"
    compute_backend: ComputeBackend = "auto"

    tool_policy: ToolPolicy = "restricted"
    tracing_enabled: bool = True
    hitl_enabled: bool = True
    max_turns: int = 100
    tool_timeout_seconds: int = 120
    command_allowlist: tuple[str, ...] = (
        "ls",
        "cat",
        "head",
        "tail",
        "wc",
        "file",
        "stat",
        "find",
        "rg",
        "grep",
        "whoami",
        "hostname",
        "uname",
        "id",
        "ps",
        "ss",
        "ip",
        "nmap",
    )

    reference_repo_root: Path = Path("repositories/cai")
    benchmark_root: Path = Path("repositories/cai/benchmarks")
    paper_pdf: Path = Path("papers/2504.06017_CAI-An-Open-Bug-Bounty-Ready-Cybersecurity-AI.pdf")
    report_root: Path = Path("outputs/reports")
    artifact_root: Path = Path("outputs/artifacts")
    trace_root: Path = Path("outputs/traces")

    ros2_enabled: bool = False
    ros2_domain_id: int = 42
    robot_target_profile: str = "lab-sim"

    @field_validator(
        "reference_repo_root",
        "benchmark_root",
        "paper_pdf",
        "report_root",
        "artifact_root",
        "trace_root",
        mode="before",
    )
    @classmethod
    def _coerce_path(cls, value: Any) -> Path:
        return value if isinstance(value, Path) else Path(str(value))

    @field_validator("tool_timeout_seconds")
    @classmethod
    def _validate_timeout(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("tool_timeout_seconds must be positive")
        return value

    @field_validator("max_turns")
    @classmethod
    def _validate_max_turns(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("max_turns must be positive")
        return value

    @field_validator("ros2_domain_id")
    @classmethod
    def _validate_ros_domain(cls, value: int) -> int:
        if not 0 <= value <= 232:
            raise ValueError("ros2_domain_id must be between 0 and 232")
        return value

    @model_validator(mode="after")
    def _normalize_paths(self) -> "DEFCAISettings":
        if not self.benchmark_root.is_absolute():
            self.benchmark_root = (Path.cwd() / self.benchmark_root).resolve()
        if not self.reference_repo_root.is_absolute():
            self.reference_repo_root = (Path.cwd() / self.reference_repo_root).resolve()
        if not self.paper_pdf.is_absolute():
            self.paper_pdf = (Path.cwd() / self.paper_pdf).resolve()
        if not self.report_root.is_absolute():
            self.report_root = (Path.cwd() / self.report_root).resolve()
        if not self.artifact_root.is_absolute():
            self.artifact_root = (Path.cwd() / self.artifact_root).resolve()
        if not self.trace_root.is_absolute():
            self.trace_root = (Path.cwd() / self.trace_root).resolve()
        return self

    @classmethod
    def from_toml(cls, path: str | Path) -> "DEFCAISettings":
        raw_path = Path(path)
        with raw_path.open("rb") as handle:
            data = tomllib.load(handle)

        merged: dict[str, Any] = {}
        project = data.get("project", {})
        merged["module_name"] = project.get("name", cls.model_fields["module_name"].default)
        merged["codename"] = project.get("codename", cls.model_fields["codename"].default)
        merged["paper_arxiv"] = project.get("paper_arxiv", cls.model_fields["paper_arxiv"].default)
        merged["python_version"] = str(
            project.get("python_version", cls.model_fields["python_version"].default)
        )

        runtime = data.get("runtime", {})
        merged["model_backend"] = runtime.get(
            "model_backend", cls.model_fields["model_backend"].default
        )
        merged["model_name"] = runtime.get("model_name", cls.model_fields["model_name"].default)
        merged["compute_backend"] = runtime.get(
            "compute_backend", cls.model_fields["compute_backend"].default
        )
        merged["tracing_enabled"] = runtime.get(
            "tracing_enabled", cls.model_fields["tracing_enabled"].default
        )
        merged["hitl_enabled"] = runtime.get(
            "hitl_enabled", cls.model_fields["hitl_enabled"].default
        )
        merged["max_turns"] = runtime.get("max_turns", cls.model_fields["max_turns"].default)
        merged["tool_timeout_seconds"] = runtime.get(
            "tool_timeout_seconds", cls.model_fields["tool_timeout_seconds"].default
        )

        safety = data.get("safety", {})
        merged["tool_policy"] = safety.get("tool_policy", cls.model_fields["tool_policy"].default)
        merged["command_allowlist"] = tuple(
            safety.get("command_allowlist", cls.model_fields["command_allowlist"].default)
        )

        paths = data.get("paths", {})
        for key in (
            "reference_repo_root",
            "benchmark_root",
            "paper_pdf",
            "report_root",
            "artifact_root",
            "trace_root",
        ):
            if key in paths:
                merged[key] = paths[key]

        ros2 = data.get("ros2", {})
        merged["ros2_enabled"] = ros2.get("enabled", cls.model_fields["ros2_enabled"].default)
        merged["ros2_domain_id"] = ros2.get("domain_id", cls.model_fields["ros2_domain_id"].default)
        merged["robot_target_profile"] = ros2.get(
            "robot_target_profile", cls.model_fields["robot_target_profile"].default
        )
        return cls(**merged)
