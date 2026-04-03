"""Minimal service scaffold for autopilot infra checks."""

from __future__ import annotations

from .settings import DEFCAISettings


def build_manifest() -> dict[str, object]:
    settings = DEFCAISettings()
    return {
        "module": settings.module_name,
        "paper_arxiv": settings.paper_arxiv,
        "model_backend": settings.model_backend,
        "tool_policy": settings.tool_policy,
        "ros2_enabled": settings.ros2_enabled,
    }


def main() -> int:
    manifest = build_manifest()
    print("DEF-CAI service scaffold ready")
    print(manifest)
    return 0
