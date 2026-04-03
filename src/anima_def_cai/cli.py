"""Typer CLI for running local DEF-CAI sessions."""

from __future__ import annotations

from pathlib import Path

import typer

from anima_def_cai.runtime.session import SessionRequest, run_session
from anima_def_cai.settings import DEFCAISettings

app = typer.Typer(help="Run local DEF-CAI sessions")


@app.callback()
def main_callback() -> None:
    """Expose the CLI as a command group even with a single subcommand."""


@app.command()
def run(
    objective: str,
    agent: str | None = typer.Option(None, "--agent", help="Single agent to run"),
    pattern: str | None = typer.Option(None, "--pattern", help="Named pattern preset"),
    config: Path = typer.Option(Path("configs/default.toml"), "--config"),
    output_root: Path | None = typer.Option(None, "--output-root"),
) -> None:
    settings = DEFCAISettings.from_toml(config)
    result = run_session(
        SessionRequest(
            objective=objective,
            agent_name=agent,
            pattern_name=pattern,
            output_root=output_root,
        ),
        settings,
    )
    typer.echo(f"Trace: {result.state.trace_id}")
    typer.echo(f"Turns: {result.summary.turns_executed}")
    typer.echo(f"Artifacts: {result.artifact_dir}")


def main() -> int:
    app()
    return 0
