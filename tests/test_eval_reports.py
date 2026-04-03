"""Tests for evaluation report rendering and paper-delta summary."""

from __future__ import annotations

import json

import pytest

from anima_def_cai.eval.metrics import compute_metrics
from anima_def_cai.eval.paper_delta import (
    PAPER_CLAIMS,
    ReproductionStatus,
    render_paper_delta_markdown,
    summarize_paper_delta,
)
from anima_def_cai.eval.runner import (
    EvalReport,
    EvalResult,
    SampleOutcome,
)
from anima_def_cai.reports.eval_report import render_eval_json, render_eval_markdown


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


class TestComputeMetrics:
    def test_empty_results(self) -> None:
        m = compute_metrics([], budget=100)
        assert m.total_samples == 0
        assert m.pass_at_1 == 0.0

    def test_all_pass(self) -> None:
        results = [
            EvalResult(
                sample_id=f"s-{i}",
                outcome=SampleOutcome.PASS,
                interactions_used=5,
                elapsed_seconds=1.0,
                usd_cost=0.01,
            )
            for i in range(10)
        ]
        m = compute_metrics(results, budget=100)
        assert m.passed == 10
        assert m.pass_at_1 == 1.0
        assert m.pass_100_at_1 == 1.0
        assert m.total_elapsed_seconds == pytest.approx(10.0)
        assert m.total_usd_cost == pytest.approx(0.1)

    def test_mixed_outcomes(self) -> None:
        results = [
            EvalResult(sample_id="a", outcome=SampleOutcome.PASS, interactions_used=5),
            EvalResult(sample_id="b", outcome=SampleOutcome.FAIL, interactions_used=50),
            EvalResult(sample_id="c", outcome=SampleOutcome.ERROR, error_message="boom"),
            EvalResult(sample_id="d", outcome=SampleOutcome.SKIPPED),
        ]
        m = compute_metrics(results, budget=100)
        assert m.total_samples == 4
        assert m.passed == 1
        assert m.failed == 1
        assert m.errors == 1
        assert m.skipped == 1
        # pass@1 computed over evaluated (pass + fail) = 1/2
        assert m.pass_at_1 == 0.5

    def test_pass100_budget_filter(self) -> None:
        results = [
            EvalResult(sample_id="in", outcome=SampleOutcome.PASS, interactions_used=50),
            EvalResult(sample_id="over", outcome=SampleOutcome.PASS, interactions_used=150),
            EvalResult(sample_id="fail", outcome=SampleOutcome.FAIL, interactions_used=10),
        ]
        m = compute_metrics(results, budget=100)
        # pass@1: 2 pass / 3 evaluated
        assert m.pass_at_1 == pytest.approx(2 / 3, abs=0.001)
        # pass100@1: only 1 within budget / 3 evaluated
        assert m.pass_100_at_1 == pytest.approx(1 / 3, abs=0.001)


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------


class TestRenderEvalMarkdown:
    def _make_report(self) -> EvalReport:
        results = [
            EvalResult(
                sample_id="s-0",
                outcome=SampleOutcome.PASS,
                model_answer="B",
                expected_answer="B",
                elapsed_seconds=1.5,
                interactions_used=3,
                usd_cost=0.005,
            ),
            EvalResult(
                sample_id="s-1",
                outcome=SampleOutcome.FAIL,
                model_answer="A",
                expected_answer="C",
                elapsed_seconds=2.0,
                interactions_used=10,
                usd_cost=0.01,
            ),
        ]
        metrics = compute_metrics(results, budget=100)
        return EvalReport(
            benchmark="cybermetric",
            model_backend="openai",
            model_name="gpt-4o",
            agent_pattern="red_blue",
            interaction_budget=100,
            total_samples=2,
            results=results,
            metrics=metrics,
            tags=["test"],
        )

    def test_contains_header(self) -> None:
        md = render_eval_markdown(self._make_report())
        assert "# DEF-CAI Evaluation Report" in md

    def test_contains_metrics_table(self) -> None:
        md = render_eval_markdown(self._make_report())
        assert "pass@1" in md
        assert "pass100@1" in md

    def test_contains_sample_rows(self) -> None:
        md = render_eval_markdown(self._make_report())
        assert "s-0" in md
        assert "s-1" in md

    def test_contains_tags(self) -> None:
        md = render_eval_markdown(self._make_report())
        assert "`test`" in md


class TestRenderEvalJSON:
    def test_valid_json(self) -> None:
        report = EvalReport(
            benchmark="cybermetric",
            model_backend="mock",
            model_name="mock",
            agent_pattern="red_blue",
            interaction_budget=100,
            total_samples=0,
        )
        text = render_eval_json(report)
        parsed = json.loads(text)
        assert parsed["benchmark"] == "cybermetric"
        assert isinstance(parsed["results"], list)


# ---------------------------------------------------------------------------
# Paper delta
# ---------------------------------------------------------------------------


class TestPaperDelta:
    def test_summary_structure(self) -> None:
        s = summarize_paper_delta()
        assert s["total_claims"] == len(PAPER_CLAIMS)
        assert s["full"] >= 1
        assert s["blocked"] >= 1
        assert isinstance(s["claims"], list)

    def test_all_statuses_valid(self) -> None:
        for claim in PAPER_CLAIMS:
            assert claim.status in ReproductionStatus

    def test_markdown_render(self) -> None:
        md = render_paper_delta_markdown()
        assert "Paper Reproduction Delta" in md
        assert "full" in md
        assert "blocked" in md
