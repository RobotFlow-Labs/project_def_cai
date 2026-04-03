#!/usr/bin/env python3
"""DEF-CAI Benchmark Runner — the "training" equivalent for this framework module.

Runs all available benchmarks (CyberMetric, SecEval, CTI-Bench, CyberPII),
generates reports, and saves artifacts to /mnt/artifacts-datai/.

This is a code-only framework — no GPU weight training. The benchmarks
exercise the evaluation pipeline and produce reproducibility evidence.

Usage:
    CUDA_VISIBLE_DEVICES=1 uv run python scripts/run_benchmarks.py
    uv run python scripts/run_benchmarks.py --benchmark cybermetric
    uv run python scripts/run_benchmarks.py --all
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

# Project root — must be before module imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from anima_def_cai.eval.datasets import BenchmarkType, list_datasets  # noqa: E402
from anima_def_cai.eval.paper_delta import render_paper_delta_markdown, summarize_paper_delta  # noqa: E402
from anima_def_cai.eval.runner import (  # noqa: E402
    EvalConfig,
    EvalReport,
    EvalResult,
    SampleOutcome,
    run_benchmark,
)
from anima_def_cai.reports.eval_report import render_eval_json, render_eval_markdown  # noqa: E402

# Output dirs
MODULE_NAME = "project_def_cai"
ARTIFACTS_ROOT = Path(os.environ.get("ARTIFACTS_ROOT", "/mnt/artifacts-datai"))
REPORT_DIR = ARTIFACTS_ROOT / "reports" / MODULE_NAME
LOG_DIR = ARTIFACTS_ROOT / "logs" / MODULE_NAME


class ExactMatchSolver:
    """Solver that checks if the sample has a known answer and grades it.

    For benchmarks like CyberMetric/SecEval with multiple-choice answers,
    this simulates a "ground truth" run by echoing the answer back.
    Useful for validating the pipeline end-to-end.
    """

    def solve(
        self,
        sample,
        *,
        budget: int = 100,
        model_backend: str = "exact_match",
        model_name: str = "ground_truth",
    ) -> EvalResult:
        if sample.answer:
            return EvalResult(
                sample_id=sample.id,
                outcome=SampleOutcome.PASS,
                model_answer=sample.answer,
                expected_answer=sample.answer,
                interactions_used=1,
                usd_cost=0.0,
            )
        return EvalResult(
            sample_id=sample.id,
            outcome=SampleOutcome.SKIPPED,
            expected_answer="",
            metadata={"reason": "no_ground_truth"},
        )


def run_single_benchmark(benchmark: str, solver=None) -> EvalReport:
    """Run a single benchmark and return the report."""
    solver = solver or ExactMatchSolver()
    cfg = EvalConfig(
        benchmark=BenchmarkType(benchmark),
        model_backend="exact_match",
        model_name="ground_truth",
        interaction_budget=100,
        tags=["pipeline_validation", benchmark],
    )
    return run_benchmark(cfg, solver=solver, project_root=PROJECT_ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description="DEF-CAI Benchmark Runner")
    parser.add_argument("--benchmark", "-b", help="Single benchmark to run")
    parser.add_argument("--all", action="store_true", help="Run all benchmarks")
    parser.add_argument("--output-dir", "-o", type=Path, default=REPORT_DIR)
    args = parser.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Print config
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    print("=" * 70)
    print(f"DEF-CAI Benchmark Runner — {timestamp}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Output dir:   {args.output_dir}")
    print("=" * 70)

    # Check available datasets
    info = list_datasets(project_root=PROJECT_ROOT)
    available = [b for b, d in info.items() if d["files_available"] > 0]
    print(f"\nAvailable benchmarks: {', '.join(available)}")

    # Decide which benchmarks to run
    if args.benchmark:
        benchmarks = [args.benchmark]
    elif args.all:
        benchmarks = available
    else:
        benchmarks = available  # default: run all available

    total_start = perf_counter()
    reports: list[EvalReport] = []
    solver = ExactMatchSolver()

    for bench in benchmarks:
        print(f"\n{'─' * 50}")
        print(f"Running: {bench}")
        print(f"{'─' * 50}")

        t0 = perf_counter()
        report = run_single_benchmark(bench, solver=solver)
        elapsed = perf_counter() - t0

        reports.append(report)

        m = report.metrics
        if m:
            print(f"  Samples: {m.total_samples}")
            print(f"  Passed:  {m.passed}  Failed: {m.failed}  Skipped: {m.skipped}")
            print(f"  pass@1:  {m.pass_at_1:.4f}")
            print(f"  Time:    {elapsed:.2f}s")

        # Save individual report
        report_path = args.output_dir / f"eval_{bench}_{timestamp}.json"
        report_path.write_text(render_eval_json(report), encoding="utf-8")

        md_path = args.output_dir / f"eval_{bench}_{timestamp}.md"
        md_path.write_text(render_eval_markdown(report), encoding="utf-8")
        print(f"  Report:  {report_path}")

    total_elapsed = perf_counter() - total_start

    # Summary
    print(f"\n{'=' * 70}")
    print("BENCHMARK SUMMARY")
    print(f"{'=' * 70}")
    total_samples = sum(r.total_samples for r in reports)
    total_passed = sum(r.metrics.passed for r in reports if r.metrics)
    total_failed = sum(r.metrics.failed for r in reports if r.metrics)
    total_skipped = sum(r.metrics.skipped for r in reports if r.metrics)
    print(f"Benchmarks run: {len(reports)}")
    print(f"Total samples:  {total_samples}")
    print(f"Passed:         {total_passed}")
    print(f"Failed:         {total_failed}")
    print(f"Skipped:        {total_skipped}")
    print(f"Total time:     {total_elapsed:.2f}s")

    # Paper delta
    print(f"\n{'─' * 50}")
    print(render_paper_delta_markdown())

    # Save combined summary
    summary = {
        "timestamp": timestamp,
        "benchmarks_run": len(reports),
        "total_samples": total_samples,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_skipped": total_skipped,
        "total_elapsed_seconds": round(total_elapsed, 3),
        "paper_delta": summarize_paper_delta(),
        "individual_reports": [r.run_id for r in reports],
    }
    summary_path = args.output_dir / f"benchmark_summary_{timestamp}.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSummary saved: {summary_path}")
    print(f"{'=' * 70}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
