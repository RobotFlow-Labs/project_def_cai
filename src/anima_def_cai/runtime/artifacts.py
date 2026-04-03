"""Artifact persistence for findings and traces."""

from __future__ import annotations

from pathlib import Path

from anima_def_cai.reports.findings import render_findings, render_findings_json
from anima_def_cai.schemas import FindingRecord


def write_artifacts(
    trace_id: str,
    findings: list[FindingRecord],
    root: Path | None = None,
) -> Path:
    artifact_dir = (root or Path("outputs/artifacts")) / trace_id
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "findings.md").write_text(render_findings(findings), encoding="utf-8")
    (artifact_dir / "findings.json").write_text(
        render_findings_json(findings),
        encoding="utf-8",
    )
    return artifact_dir
