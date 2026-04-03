"""Finding rendering utilities."""

from __future__ import annotations

import json

from anima_def_cai.schemas import FindingRecord


def render_findings(findings: list[FindingRecord]) -> str:
    lines = ["# DEF-CAI Findings", ""]
    for finding in findings:
        lines.extend(
            [
                f"## {finding.title}",
                f"- Severity: {finding.severity.value}",
                f"- Kind: {finding.kind.value}",
                f"- Confidence: {finding.confidence:.2f}",
                "",
                finding.summary,
                "",
            ]
        )
        if finding.reproduction:
            lines.extend(["### Reproduction", finding.reproduction, ""])
        if finding.evidence:
            lines.append("### Evidence")
            lines.extend([f"- {item}" for item in finding.evidence])
            lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_findings_json(findings: list[FindingRecord]) -> str:
    return json.dumps([finding.model_dump(mode="json") for finding in findings], indent=2)
