"""Findings and report endpoints.

Paper reference: Section 3.5 — bug bounty findings and evidence.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from anima_def_cai.eval.paper_delta import render_paper_delta_markdown, summarize_paper_delta

router = APIRouter()


@router.get("/paper-delta")
async def paper_delta() -> dict[str, Any]:
    return summarize_paper_delta()


@router.get("/paper-delta/markdown")
async def paper_delta_markdown() -> dict[str, str]:
    return {"markdown": render_paper_delta_markdown()}
