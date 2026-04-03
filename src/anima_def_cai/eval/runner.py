"""CAIBench-style evaluation runner.

Orchestrates benchmark execution: loads a dataset, runs each sample through
the CAI session runtime (or a pluggable solver), and collects per-sample
results for downstream metrics and reporting.

Paper reference: Section 3.1-3.2 — "We measure CAI performance using the
pass@1 metric ... a maximum limit of 100 interactions ... pass100@1."
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from time import perf_counter
from typing import Any, Protocol

import tomllib
from pydantic import BaseModel, Field, field_validator

from anima_def_cai.eval.datasets import BenchmarkSample, BenchmarkType, load_dataset
from anima_def_cai.eval.metrics import EvalMetricsSummary, compute_metrics
from anima_def_cai.settings import DEFCAISettings


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class EvalConfig(BaseModel):
    """Configuration for a single benchmark run."""

    benchmark: BenchmarkType
    model_backend: str = "openai"
    model_name: str = "gpt-4o-2024-11-20"
    interaction_budget: int = 100
    dataset_file: Path | None = None
    agent_pattern: str = "red_blue"
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("interaction_budget")
    @classmethod
    def _validate_budget(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("interaction_budget must be positive")
        return value

    @classmethod
    def from_toml(cls, path: str | Path) -> "EvalConfig":
        with Path(path).open("rb") as fh:
            data = tomllib.load(fh)
        flat: dict[str, Any] = {}
        flat["benchmark"] = data.get("benchmark", data.get("eval", {}).get("benchmark"))
        for key in (
            "model_backend",
            "model_name",
            "interaction_budget",
            "dataset_file",
            "agent_pattern",
            "tags",
        ):
            section = data.get("eval", data)
            if key in section:
                flat[key] = section[key]
            elif key in data:
                flat[key] = data[key]
        flat = {k: v for k, v in flat.items() if v is not None}
        return cls(**flat)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


class SampleOutcome(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    SKIPPED = "skipped"


class EvalResult(BaseModel):
    """Result for a single benchmark sample."""

    sample_id: str
    outcome: SampleOutcome
    model_answer: str = ""
    expected_answer: str = ""
    elapsed_seconds: float = 0.0
    interactions_used: int = 0
    usd_cost: float = 0.0
    error_message: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvalReport(BaseModel):
    """Full benchmark run report."""

    run_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    benchmark: BenchmarkType
    model_backend: str
    model_name: str
    agent_pattern: str
    interaction_budget: int
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    total_samples: int = 0
    results: list[EvalResult] = Field(default_factory=list)
    metrics: EvalMetricsSummary | None = None
    tags: list[str] = Field(default_factory=list)
    config_snapshot: dict[str, Any] = Field(default_factory=dict)

    @property
    def duration_seconds(self) -> float:
        if self.finished_at and self.started_at:
            return (self.finished_at - self.started_at).total_seconds()
        return 0.0


# ---------------------------------------------------------------------------
# Solver protocol — pluggable per-sample execution
# ---------------------------------------------------------------------------


class SampleSolver(Protocol):
    """Pluggable interface so callers can swap the actual LLM execution."""

    def solve(
        self,
        sample: BenchmarkSample,
        *,
        budget: int,
        model_backend: str,
        model_name: str,
    ) -> EvalResult: ...


class DefaultSolver:
    """Stub solver that performs exact-match grading without LLM calls.

    Useful for smoke tests and offline evaluation of pre-computed answers.
    For live LLM evaluation, inject a real solver via ``run_benchmark``.
    """

    def solve(
        self,
        sample: BenchmarkSample,
        *,
        budget: int = 100,
        model_backend: str = "mock",
        model_name: str = "mock",
    ) -> EvalResult:
        return EvalResult(
            sample_id=sample.id,
            outcome=SampleOutcome.SKIPPED,
            model_answer="",
            expected_answer=sample.answer,
            interactions_used=0,
            metadata={"reason": "default_solver_stub"},
        )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run_benchmark(
    config: EvalConfig,
    *,
    settings: DEFCAISettings | None = None,
    solver: SampleSolver | None = None,
    project_root: Path | None = None,
) -> EvalReport:
    """Execute a full benchmark run and return a populated :class:`EvalReport`.

    Parameters
    ----------
    config:
        Evaluation configuration (benchmark type, budget, model, etc.).
    settings:
        DEF-CAI runtime settings.  Defaults are used when ``None``.
    solver:
        Pluggable per-sample executor.  Falls back to :class:`DefaultSolver`.
    project_root:
        Project root for dataset resolution.
    """
    settings = settings or DEFCAISettings()
    solver = solver or DefaultSolver()
    root = project_root or Path.cwd()

    samples = load_dataset(
        config.benchmark,
        project_root=root,
        file_override=config.dataset_file,
    )

    report = EvalReport(
        benchmark=config.benchmark,
        model_backend=config.model_backend,
        model_name=config.model_name,
        agent_pattern=config.agent_pattern,
        interaction_budget=config.interaction_budget,
        total_samples=len(samples),
        tags=list(config.tags),
        config_snapshot=config.model_dump(mode="json"),
    )

    for sample in samples:
        t0 = perf_counter()
        try:
            result = solver.solve(
                sample,
                budget=config.interaction_budget,
                model_backend=config.model_backend,
                model_name=config.model_name,
            )
            result.elapsed_seconds = perf_counter() - t0
        except Exception as exc:  # noqa: BLE001
            result = EvalResult(
                sample_id=sample.id,
                outcome=SampleOutcome.ERROR,
                expected_answer=sample.answer,
                elapsed_seconds=perf_counter() - t0,
                error_message=str(exc),
            )
        report.results.append(result)

    report.finished_at = datetime.now(timezone.utc)
    report.metrics = compute_metrics(report.results, budget=config.interaction_budget)
    return report
