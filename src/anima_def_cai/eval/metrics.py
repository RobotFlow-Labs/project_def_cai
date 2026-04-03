"""Pass@1, pass100@1, time, and cost metrics for CAIBench evaluation.

Paper reference: Tables 2-4 — "pass@1 metric", "pass100@1", time and cost
columns across models.

These helpers are intentionally import-light so that ``runner.py`` can import
them without circular dependencies.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EvalMetricsSummary(BaseModel):
    """Aggregated metrics for a benchmark run."""

    total_samples: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0

    pass_at_1: float = 0.0
    pass_100_at_1: float = 0.0

    total_elapsed_seconds: float = 0.0
    mean_elapsed_seconds: float = 0.0

    total_usd_cost: float = 0.0
    mean_usd_cost: float = 0.0

    total_interactions: int = 0
    mean_interactions: float = 0.0

    interaction_budget: int = 100
    per_outcome: dict[str, int] = Field(default_factory=dict)


def compute_metrics(
    results: list[Any],
    *,
    budget: int = 100,
) -> EvalMetricsSummary:
    """Compute aggregate metrics from a list of :class:`EvalResult` objects.

    Parameters
    ----------
    results:
        List of ``EvalResult`` instances (imported as Any to avoid circular
        import with ``runner.py``).
    budget:
        Interaction budget used for this run (for pass100@1 denominator).
    """
    total = len(results)
    if total == 0:
        return EvalMetricsSummary(interaction_budget=budget)

    passed = sum(1 for r in results if r.outcome == "pass")
    failed = sum(1 for r in results if r.outcome == "fail")
    errors = sum(1 for r in results if r.outcome == "error")
    skipped = sum(1 for r in results if r.outcome == "skipped")

    evaluated = passed + failed  # exclude errors/skipped from pass rate
    pass_at_1 = passed / evaluated if evaluated > 0 else 0.0

    # pass100@1: pass rate limited to samples solved within `budget` interactions
    within_budget = sum(1 for r in results if r.outcome == "pass" and r.interactions_used <= budget)
    pass_100_at_1 = within_budget / evaluated if evaluated > 0 else 0.0

    total_elapsed = sum(r.elapsed_seconds for r in results)
    total_cost = sum(r.usd_cost for r in results)
    total_interactions = sum(r.interactions_used for r in results)

    per_outcome: dict[str, int] = {}
    for r in results:
        outcome_str = str(r.outcome)
        per_outcome[outcome_str] = per_outcome.get(outcome_str, 0) + 1

    return EvalMetricsSummary(
        total_samples=total,
        passed=passed,
        failed=failed,
        errors=errors,
        skipped=skipped,
        pass_at_1=round(pass_at_1, 4),
        pass_100_at_1=round(pass_100_at_1, 4),
        total_elapsed_seconds=round(total_elapsed, 3),
        mean_elapsed_seconds=round(total_elapsed / total, 3),
        total_usd_cost=round(total_cost, 6),
        mean_usd_cost=round(total_cost / total, 6),
        total_interactions=total_interactions,
        mean_interactions=round(total_interactions / total, 2),
        interaction_budget=budget,
        per_outcome=per_outcome,
    )
