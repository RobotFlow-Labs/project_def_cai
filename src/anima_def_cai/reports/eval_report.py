"""Markdown and JSON report rendering for CAIBench evaluation runs.

Emits a human-readable markdown summary alongside a machine-readable JSON
blob.  Reports clearly distinguish which paper claims are fully reproduced
vs approximated (driven by the paper-delta helper in ``eval.paper_delta``).

Paper reference: Section 3, Tables 2-4.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anima_def_cai.eval.runner import EvalReport


def render_eval_markdown(report: "EvalReport") -> str:
    """Render a markdown evaluation report."""
    lines: list[str] = [
        "# DEF-CAI Evaluation Report",
        "",
        f"- **Run ID**: `{report.run_id}`",
        f"- **Benchmark**: {report.benchmark.value}",
        f"- **Model**: {report.model_backend}/{report.model_name}",
        f"- **Pattern**: {report.agent_pattern}",
        f"- **Interaction budget**: {report.interaction_budget}",
        f"- **Total samples**: {report.total_samples}",
        f"- **Duration**: {report.duration_seconds:.1f}s",
        "",
    ]

    metrics = report.metrics
    if metrics:
        lines.extend(
            [
                "## Metrics",
                "",
                "| Metric | Value |",
                "|---|---|",
                f"| pass@1 | {metrics.pass_at_1:.4f} |",
                f"| pass100@1 | {metrics.pass_100_at_1:.4f} |",
                f"| Passed | {metrics.passed} |",
                f"| Failed | {metrics.failed} |",
                f"| Errors | {metrics.errors} |",
                f"| Skipped | {metrics.skipped} |",
                f"| Total elapsed (s) | {metrics.total_elapsed_seconds:.1f} |",
                f"| Mean elapsed (s) | {metrics.mean_elapsed_seconds:.3f} |",
                f"| Total cost (USD) | ${metrics.total_usd_cost:.4f} |",
                f"| Mean cost (USD) | ${metrics.mean_usd_cost:.6f} |",
                f"| Total interactions | {metrics.total_interactions} |",
                f"| Mean interactions | {metrics.mean_interactions:.1f} |",
                "",
            ]
        )

    if report.results:
        lines.extend(
            [
                "## Sample Results",
                "",
                "| Sample | Outcome | Expected | Model Answer | Time (s) | Interactions |",
                "|---|---|---|---|---|---|",
            ]
        )
        for r in report.results:
            expected = r.expected_answer[:30] if r.expected_answer else "-"
            model_ans = r.model_answer[:30] if r.model_answer else "-"
            lines.append(
                f"| {r.sample_id} | {r.outcome.value} | {expected} "
                f"| {model_ans} | {r.elapsed_seconds:.2f} | {r.interactions_used} |"
            )
        lines.append("")

    if report.tags:
        lines.extend(["## Tags", "", ", ".join(f"`{t}`" for t in report.tags), ""])

    return "\n".join(lines).rstrip() + "\n"


def render_eval_json(report: "EvalReport") -> str:
    """Render a machine-readable JSON evaluation report."""
    return json.dumps(report.model_dump(mode="json"), indent=2, default=str)
