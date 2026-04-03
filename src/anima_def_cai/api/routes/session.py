"""Session endpoints — run CAI-style agent sessions.

Paper reference: Section 2 — agent orchestration and tool integration.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter
from pydantic import BaseModel

from anima_def_cai.api.deps import get_settings
from anima_def_cai.runtime.session import SessionRequest, run_session

router = APIRouter()


class SessionRunRequest(BaseModel):
    objective: str
    agent_name: str | None = None
    pattern_name: str | None = None


class SessionRunResponse(BaseModel):
    trace_id: str
    status: str
    findings_count: int
    turns_executed: int
    duration_seconds: float
    artifact_dir: str
    latest_message: str = ""


@router.post("/run")
async def run(req: SessionRunRequest) -> SessionRunResponse:
    settings = get_settings()
    session_req = SessionRequest(
        objective=req.objective,
        agent_name=req.agent_name,
        pattern_name=req.pattern_name,
    )
    result = await asyncio.to_thread(run_session, session_req, settings)
    latest_msg = ""
    if result.state.messages:
        latest_msg = result.state.messages[-1].content[:500]
    return SessionRunResponse(
        trace_id=result.state.trace_id,
        status="interrupted" if result.state.interrupted else "completed",
        findings_count=len(result.state.findings),
        turns_executed=result.summary.turns_executed,
        duration_seconds=result.summary.duration_seconds,
        artifact_dir=str(result.artifact_dir),
        latest_message=latest_msg,
    )
