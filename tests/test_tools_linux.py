from anima_def_cai.settings import DEFCAISettings
from anima_def_cai.tools import execute_python, run_linux_command


def test_linux_command_runs_allowlisted_binary() -> None:
    observation = run_linux_command('python3 -c "print(\'ok\')"', settings=DEFCAISettings())
    assert observation.exit_code == 0
    assert "ok" in observation.stdout


def test_linux_command_blocks_disallowed_binary() -> None:
    observation = run_linux_command("rm -rf /tmp/forbidden", settings=DEFCAISettings())
    assert observation.allowed is False
    assert observation.exit_code == 126


def test_execute_python_returns_output() -> None:
    observation = execute_python("print('hello from code')")
    assert observation.exit_code == 0
    assert "hello from code" in observation.stdout
