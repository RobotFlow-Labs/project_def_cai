#!/usr/bin/env python3
"""Framework-oriented training placeholder for autopilot compatibility."""

from __future__ import annotations

from anima_def_cai.settings import DEFCAISettings


def main() -> int:
    settings = DEFCAISettings()
    print(
        "DEF-CAI is a framework/orchestration module. No weight training is defined in the "
        f"paper; use benchmark/evaluation workflows after build. Active backend={settings.compute_backend}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
