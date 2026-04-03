"""Shared API dependencies."""

from __future__ import annotations

from anima_def_cai.settings import DEFCAISettings

_settings: DEFCAISettings | None = None


def get_settings() -> DEFCAISettings:
    global _settings
    if _settings is None:
        _settings = DEFCAISettings()
    return _settings


def set_settings(settings: DEFCAISettings) -> None:
    global _settings
    _settings = settings
