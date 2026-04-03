"""Paper-delta summary: track which CAI paper claims are reproduced.

For each paper benchmark or claim, this module records whether DEF-CAI can
fully reproduce it, partially approximate it, or is blocked by unavailable
private assets.

Paper reference: §3.1-3.2, Tables 2-4.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class ReproductionStatus(StrEnum):
    FULL = "full"
    PARTIAL = "partial"
    BLOCKED = "blocked"
    NOT_ATTEMPTED = "not_attempted"


class PaperClaim(BaseModel):
    """A single paper claim or benchmark with reproduction status."""

    claim_id: str
    description: str
    paper_section: str
    status: ReproductionStatus
    reason: str
    our_value: str = ""
    paper_value: str = ""


# ---------------------------------------------------------------------------
# Static registry of paper claims vs our ability to reproduce
# ---------------------------------------------------------------------------

PAPER_CLAIMS: list[PaperClaim] = [
    PaperClaim(
        claim_id="cybermetric_knowledge",
        description="CyberMetric-2 knowledge benchmark pass@1 across models",
        paper_section="§3.1, Table 2",
        status=ReproductionStatus.FULL,
        reason="CyberMetric-2-v1.json is available locally in the reference repo",
        paper_value="See Table 2 for per-model scores",
    ),
    PaperClaim(
        claim_id="seceval_knowledge",
        description="SecEval security knowledge benchmark pass@1",
        paper_section="§3.1, Table 2",
        status=ReproductionStatus.FULL,
        reason="SecEval question sets available locally",
        paper_value="See Table 2 for per-model scores",
    ),
    PaperClaim(
        claim_id="cti_bench_knowledge",
        description="CTI-Bench cyber threat intelligence benchmark",
        paper_section="§3.1, Table 3",
        status=ReproductionStatus.FULL,
        reason="CTI-Bench TSV files available locally",
        paper_value="See Table 3 for per-model scores",
    ),
    PaperClaim(
        claim_id="cyberpii_privacy",
        description="CyberPII-Bench PII detection and anonymisation",
        paper_section="§3.2",
        status=ReproductionStatus.FULL,
        reason="CyberPII-Bench gold CSV available locally",
        paper_value="Entity-level precision/recall/F1",
    ),
    PaperClaim(
        claim_id="htb_ctf_54",
        description="54 Hack The Box CTF exercise pass100@1",
        paper_section="§3.1, Table 4",
        status=ReproductionStatus.BLOCKED,
        reason="HTB competition infrastructure is private; exact challenges unavailable",
        paper_value="Table 4: model-specific pass100@1 scores",
    ),
    PaperClaim(
        claim_id="bug_bounty_evidence",
        description="Bug bounty submissions and payouts",
        paper_section="§4",
        status=ReproductionStatus.BLOCKED,
        reason="Real bug bounty targets and disclosed findings are private",
        paper_value="Reported bounties across multiple programs",
    ),
    PaperClaim(
        claim_id="robot_security_case",
        description="Robot security case studies (MIR, ROS, MQTT)",
        paper_section="§5",
        status=ReproductionStatus.PARTIAL,
        reason=(
            "Architectural patterns reproduced; exact hardware targets require "
            "physical robot lab or simulation environment"
        ),
        paper_value="Demonstrated vulnerabilities in MIR robots",
    ),
    PaperClaim(
        claim_id="cost_comparison",
        description="Time and cost comparison across models",
        paper_section="§3, Tables 2-4",
        status=ReproductionStatus.FULL,
        reason="Cost/time metering is implemented in the runner; actual costs depend on API pricing",
        paper_value="Per-model USD cost and wall-clock time",
    ),
]


def summarize_paper_delta() -> dict[str, Any]:
    """Return a structured summary of paper reproduction status."""
    by_status: dict[str, list[str]] = {s.value: [] for s in ReproductionStatus}
    for claim in PAPER_CLAIMS:
        by_status[claim.status.value].append(claim.claim_id)

    return {
        "total_claims": len(PAPER_CLAIMS),
        "full": len(by_status["full"]),
        "partial": len(by_status["partial"]),
        "blocked": len(by_status["blocked"]),
        "not_attempted": len(by_status["not_attempted"]),
        "by_status": by_status,
        "claims": [c.model_dump() for c in PAPER_CLAIMS],
    }


def render_paper_delta_markdown() -> str:
    """Render a markdown summary of paper delta status."""
    lines: list[str] = [
        "# Paper Reproduction Delta",
        "",
        "| Claim | Section | Status | Reason |",
        "|---|---|---|---|",
    ]
    for claim in PAPER_CLAIMS:
        icon = {"full": "OK", "partial": "~", "blocked": "X", "not_attempted": "-"}
        lines.append(
            f"| {claim.description} | {claim.paper_section} "
            f"| {icon.get(claim.status.value, '?')} {claim.status.value} | {claim.reason} |"
        )
    summary = summarize_paper_delta()
    lines.extend(
        [
            "",
            f"**Total**: {summary['total_claims']} claims — "
            f"{summary['full']} full, {summary['partial']} partial, "
            f"{summary['blocked']} blocked, {summary['not_attempted']} not attempted",
            "",
        ]
    )
    return "\n".join(lines)
