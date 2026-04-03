"""Code execution helpers."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from .common import ToolObservation


def execute_python(code: str, timeout: int = 30) -> ToolObservation:
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
            artifact_paths=[script],
        )
