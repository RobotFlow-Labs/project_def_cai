"""DEF-CAI service entrypoint — FastAPI + uvicorn.

Launches the ANIMA-standard health/ready/info + module-specific endpoints.
"""

from __future__ import annotations

import os

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
    import uvicorn

    from .api.app import create_app

    port = int(os.environ.get("ANIMA_SERVE_PORT", "8080"))
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
