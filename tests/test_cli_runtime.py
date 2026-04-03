from pathlib import Path

from typer.testing import CliRunner

from anima_def_cai.cli import app
from anima_def_cai.runtime.session import pause_and_collect
from anima_def_cai.schemas import TurnState

runner = CliRunner()


def test_cli_runs_single_agent_session(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "run",
            "inspect target",
            "--agent",
            "red_team",
            "--output-root",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert "Trace:" in result.stdout
    # Dynamic trace ID — check that at least one trace dir was created
    trace_dirs = [d for d in tmp_path.iterdir() if d.is_dir() and d.name.startswith("trace-")]
    assert len(trace_dirs) >= 1
    assert (trace_dirs[0] / "findings.json").exists()


def test_pause_and_collect_restores_execution() -> None:
    state = TurnState(objective="pause", trace_id="trace-cli-1", interrupted=True)
    resumed = pause_and_collect(state, operator_input="continue with red team")
    assert resumed.interrupted is False
    assert resumed.operator_override is True
    assert resumed.messages[-1].role == "operator"
