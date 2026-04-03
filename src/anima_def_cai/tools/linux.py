"""Guarded Linux command execution."""

from __future__ import annotations

import shlex
import subprocess

from .common import ToolObservation
from anima_def_cai.settings import DEFCAISettings


def run_linux_command(
    cmd: str,
    timeout: int = 30,
    settings: DEFCAISettings | None = None,
) -> ToolObservation:
    active_settings = settings or DEFCAISettings()
    parts = shlex.split(cmd)
    if not parts:
        return ToolObservation(
            tool_name="linux",
            command=cmd,
            stderr="No command provided",
            exit_code=1,
            allowed=False,
        )

    executable = parts[0]
    if executable not in active_settings.command_allowlist:
        return ToolObservation(
            tool_name="linux",
            command=cmd,
            stderr=f"Command prefix '{executable}' is blocked by tool policy",
            exit_code=126,
            allowed=False,
            metadata={"policy": active_settings.tool_policy},
        )

    completed = subprocess.run(
        parts,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return ToolObservation(
        tool_name="linux",
        command=cmd,
        stdout=completed.stdout,
        stderr=completed.stderr,
        exit_code=completed.returncode,
        allowed=True,
        metadata={"policy": active_settings.tool_policy},
    )
