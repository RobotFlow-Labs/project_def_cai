"""FastAPI application for DEF-CAI runtime and evaluation.

Exposes health, session, evaluation, and findings endpoints.
Paper reference: Section 1-2 — modular agent design with tool integration.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator

from fastapi import FastAPI

from anima_def_cai.settings import DEFCAISettings
from anima_def_cai.version import __version__

from .deps import get_settings, set_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    get_settings()
    yield


def create_app(settings: DEFCAISettings | None = None) -> FastAPI:
    if settings is not None:
        set_settings(settings)

    from .routes.eval import router as eval_router
    from .routes.findings import router as findings_router
    from .routes.session import router as session_router

    app = FastAPI(
        title="DEF-CAI",
        description="CAI-aligned cybersecurity orchestration API",
        version=__version__,
        lifespan=lifespan,
    )

    app.include_router(session_router, prefix="/sessions", tags=["sessions"])
    app.include_router(eval_router, prefix="/eval", tags=["eval"])
    app.include_router(findings_router, prefix="/findings", tags=["findings"])

    @app.get("/health")
    async def health() -> dict[str, Any]:
        s = get_settings()
        return {
            "status": "ok",
            "module": s.module_name,
            "version": __version__,
            "uptime_s": 0,
            "tool_policy": s.tool_policy,
        }

    @app.get("/ready")
    async def ready() -> dict[str, Any]:
        s = get_settings()
        return {
            "ready": True,
            "module": s.module_name,
            "version": __version__,
            "model_backend": s.model_backend,
        }

    @app.get("/info")
    async def info() -> dict[str, Any]:
        s = get_settings()
        return {
            "module": s.module_name,
            "codename": s.codename,
            "paper_arxiv": s.paper_arxiv,
            "version": __version__,
            "model_backend": s.model_backend,
            "model_name": s.model_name,
            "tool_policy": s.tool_policy,
            "ros2_enabled": s.ros2_enabled,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    return app
