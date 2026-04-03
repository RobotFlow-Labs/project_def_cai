"""Code execution helpers with guardrail integration."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from anima_def_cai.safety.guardrails import GuardrailDecision, check_command, check_input

from .common import ToolObservation


def execute_python(code: str, timeout: int = 30) -> ToolObservation:
    # Gate 1: check input for prompt injection
    input_check = check_input(code)
    if input_check.decision == GuardrailDecision.BLOCK:
        return ToolObservation(
            tool_name="code",
            command="python (blocked)",
            stderr=f"Blocked by guardrail: {input_check.reason}",
            exit_code=126,
            allowed=False,
            metadata={"guardrail_rule": input_check.rule},
        )

    # Gate 2: check for dangerous command patterns in code
    cmd_check = check_command(code)
    if cmd_check.decision == GuardrailDecision.BLOCK:
        return ToolObservation(
            tool_name="code",
            command="python (blocked)",
            stderr=f"Blocked by guardrail: {cmd_check.reason}",
            exit_code=126,
            allowed=False,
            metadata={"guardrail_rule": cmd_check.rule},
        )

    with tempfile.TemporaryDirectory(prefix="def_cai_code_") as tmpdir:
        script = Path(tmpdir) / "snippet.py"
        script.write_text(code, encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return ToolObservation(
            tool_name="code",
            command=f"{sys.executable} {script.name}",
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
            allowed=True,
            artifact_paths=[script],
        )
