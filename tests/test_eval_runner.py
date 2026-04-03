"""Tests for the evaluation runner and dataset registry."""

from __future__ import annotations

from pathlib import Path

import pytest

from anima_def_cai.eval.datasets import (
    BenchmarkSample,
    BenchmarkType,
    list_datasets,
    load_dataset,
)
from anima_def_cai.eval.runner import (
    DefaultSolver,
    EvalConfig,
    EvalReport,
    EvalResult,
    SampleOutcome,
    run_benchmark,
)

# Use the actual project root so repo-local assets resolve
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Dataset registry
# ---------------------------------------------------------------------------


class TestListDatasets:
    def test_returns_all_benchmark_types(self) -> None:
        info = list_datasets(project_root=PROJECT_ROOT)
        assert "cybermetric" in info
        assert "seceval" in info
        assert "cti_bench" in info
        assert "cyberpii" in info

    def test_file_counts_are_positive(self) -> None:
        info = list_datasets(project_root=PROJECT_ROOT)
        for bench, detail in info.items():
            assert detail["files_registered"] > 0, f"{bench} has no registered files"


# ---------------------------------------------------------------------------
# CyberMetric loader
# ---------------------------------------------------------------------------


class TestCyberMetricLoader:
    def test_loads_samples(self) -> None:
        samples = load_dataset("cybermetric", project_root=PROJECT_ROOT)
        assert len(samples) > 0

    def test_sample_fields(self) -> None:
        samples = load_dataset("cybermetric", project_root=PROJECT_ROOT)
        s = samples[0]
        assert isinstance(s, BenchmarkSample)
        assert s.benchmark == BenchmarkType.CYBERMETRIC
        assert s.question
        assert s.choices  # non-empty dict
        assert s.answer  # solution letter


# ---------------------------------------------------------------------------
# SecEval loader
# ---------------------------------------------------------------------------


class TestSecEvalLoader:
    def test_loads_samples(self) -> None:
        samples = load_dataset("seceval", project_root=PROJECT_ROOT)
        assert len(samples) > 0

    def test_sample_has_answer(self) -> None:
        samples = load_dataset("seceval", project_root=PROJECT_ROOT)
        for s in samples[:5]:
            assert s.answer, f"SecEval sample {s.id} has no answer"


# ---------------------------------------------------------------------------
# CTI-Bench loader
# ---------------------------------------------------------------------------


class TestCTIBenchLoader:
    def test_loads_samples(self) -> None:
        samples = load_dataset("cti_bench", project_root=PROJECT_ROOT)
        assert len(samples) > 0

    def test_has_four_choices(self) -> None:
        samples = load_dataset("cti_bench", project_root=PROJECT_ROOT)
        for s in samples[:5]:
            assert len(s.choices) == 4, f"CTI sample {s.id} lacks 4 choices"


# ---------------------------------------------------------------------------
# CyberPII loader
# ---------------------------------------------------------------------------


class TestCyberPIILoader:
    def test_loads_samples(self) -> None:
        samples = load_dataset("cyberpii", project_root=PROJECT_ROOT)
        assert len(samples) > 0


# ---------------------------------------------------------------------------
# EvalConfig
# ---------------------------------------------------------------------------


class TestEvalConfig:
    def test_defaults(self) -> None:
        cfg = EvalConfig(benchmark="cybermetric")
        assert cfg.interaction_budget == 100
        assert cfg.model_backend == "openai"

    def test_invalid_budget(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            EvalConfig(benchmark="cybermetric", interaction_budget=0)

    def test_from_toml(self) -> None:
        toml_path = PROJECT_ROOT / "configs" / "eval" / "knowledge.toml"
        if toml_path.exists():
            cfg = EvalConfig.from_toml(toml_path)
            assert cfg.benchmark == BenchmarkType.CYBERMETRIC
            assert cfg.interaction_budget > 0


# ---------------------------------------------------------------------------
# DefaultSolver
# ---------------------------------------------------------------------------


class TestDefaultSolver:
    def test_returns_skipped(self) -> None:
        solver = DefaultSolver()
        sample = BenchmarkSample(
            id="test-1",
            benchmark=BenchmarkType.CYBERMETRIC,
            question="What is 1+1?",
            answer="2",
        )
        result = solver.solve(sample, budget=10, model_backend="mock", model_name="mock")
        assert result.outcome == SampleOutcome.SKIPPED
        assert result.expected_answer == "2"


# ---------------------------------------------------------------------------
# run_benchmark
# ---------------------------------------------------------------------------


class TestRunBenchmark:
    def test_smoke_cybermetric(self) -> None:
        cfg = EvalConfig(benchmark="cybermetric")
        report = run_benchmark(cfg, project_root=PROJECT_ROOT)
        assert isinstance(report, EvalReport)
        assert report.total_samples > 0
        assert report.metrics is not None
        assert report.finished_at is not None

    def test_custom_solver(self) -> None:
        class AlwaysPassSolver:
            def solve(self, sample, *, budget, model_backend, model_name):
                return EvalResult(
                    sample_id=sample.id,
                    outcome=SampleOutcome.PASS,
                    model_answer=sample.answer,
                    expected_answer=sample.answer,
                    interactions_used=1,
                )

        cfg = EvalConfig(benchmark="cybermetric")
        report = run_benchmark(cfg, solver=AlwaysPassSolver(), project_root=PROJECT_ROOT)
        assert report.metrics is not None
        assert report.metrics.pass_at_1 == 1.0
        assert report.metrics.passed == report.total_samples
