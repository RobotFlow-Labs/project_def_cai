"""Shared API dependencies — thread-safe settings singleton."""

from __future__ import annotations

import threading

from anima_def_cai.settings import DEFCAISettings

_lock = threading.Lock()
_settings: DEFCAISettings | None = None


def get_settings() -> DEFCAISettings:
    global _settings
    if _settings is None:
        with _lock:
            if _settings is None:
                _settings = DEFCAISettings()
    return _settings


def set_settings(settings: DEFCAISettings) -> None:
    global _settings
    with _lock:
        _settings = settings
