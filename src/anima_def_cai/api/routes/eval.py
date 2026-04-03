"""Evaluation endpoints — run CAIBench-style benchmark evaluations.

Paper reference: Section 3.1-3.2 — pass@1, pass100@1 metrics.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from anima_def_cai.api.deps import get_settings
from anima_def_cai.eval.datasets import BenchmarkType, list_datasets
from anima_def_cai.eval.runner import EvalConfig, run_benchmark

router = APIRouter()


class EvalRunRequest(BaseModel):
    benchmark: str
    model_backend: str = "openai"
    model_name: str = "gpt-4o-2024-11-20"
    interaction_budget: int = 100
    agent_pattern: str = "red_blue"
    dataset_file: str | None = None


class EvalRunResponse(BaseModel):
    run_id: str
    benchmark: str
    total_samples: int
    passed: int
    failed: int
    pass_at_1: float
    pass_100_at_1: float
    duration_seconds: float
    total_usd_cost: float


@router.post("/run")
async def run_eval(req: EvalRunRequest) -> EvalRunResponse:
    cfg = EvalConfig(
        benchmark=BenchmarkType(req.benchmark),
        model_backend=req.model_backend,
        model_name=req.model_name,
        interaction_budget=req.interaction_budget,
        agent_pattern=req.agent_pattern,
        dataset_file=Path(req.dataset_file) if req.dataset_file else None,
    )
    report = run_benchmark(cfg, settings=get_settings())
    m = report.metrics
    return EvalRunResponse(
        run_id=report.run_id,
        benchmark=report.benchmark.value,
        total_samples=report.total_samples,
        passed=m.passed if m else 0,
        failed=m.failed if m else 0,
        pass_at_1=m.pass_at_1 if m else 0.0,
        pass_100_at_1=m.pass_100_at_1 if m else 0.0,
        duration_seconds=report.duration_seconds,
        total_usd_cost=m.total_usd_cost if m else 0.0,
    )


@router.get("/datasets")
async def datasets() -> dict[str, Any]:
    return list_datasets()
