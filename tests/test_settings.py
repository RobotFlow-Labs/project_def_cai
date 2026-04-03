from pathlib import Path

import pytest

from anima_def_cai.settings import DEFCAISettings


def test_settings_defaults_resolve_project_paths() -> None:
    settings = DEFCAISettings()
    assert settings.module_name == "def-cai"
    assert settings.paper_arxiv == "2504.06017"
    assert settings.benchmark_root.is_absolute()
    assert settings.reference_repo_root.name == "cai"


def test_settings_load_from_toml() -> None:
    settings = DEFCAISettings.from_toml(Path("configs/default.toml"))
    assert settings.module_name == "anima-def-cai"
    assert settings.compute_backend == "auto"
    assert settings.tool_policy == "restricted"
    assert settings.ros2_enabled is False


def test_settings_allow_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEF_CAI_MODEL_BACKEND", "ollama")
    monkeypatch.setenv("DEF_CAI_ROS2_ENABLED", "true")
    settings = DEFCAISettings()
    assert settings.model_backend == "ollama"
    assert settings.ros2_enabled is True


def test_invalid_turn_limits_are_rejected() -> None:
    with pytest.raises(ValueError):
        DEFCAISettings(max_turns=0)
