import json

from anima_def_cai.reports.findings import render_findings, render_findings_json
from anima_def_cai.runtime.artifacts import write_artifacts
from anima_def_cai.schemas import FindingRecord, Severity


def test_render_findings_outputs_markdown() -> None:
    finding = FindingRecord(title="Weak SSH", summary="Password auth enabled", severity=Severity.MEDIUM)
    markdown = render_findings([finding])
    assert "## Weak SSH" in markdown
    assert "Severity: medium" in markdown


def test_render_findings_json_outputs_serialized_records(tmp_path) -> None:
    finding = FindingRecord(title="Weak SSH", summary="Password auth enabled")
    payload = render_findings_json([finding])
    decoded = json.loads(payload)
    assert decoded[0]["title"] == "Weak SSH"

    artifact_dir = write_artifacts("trace-findings", [finding], root=tmp_path)
    assert (artifact_dir / "findings.md").exists()
    assert (artifact_dir / "findings.json").exists()
