"""Tests for the DEF-CAI FastAPI application."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from anima_def_cai.api.app import create_app
from anima_def_cai.settings import DEFCAISettings


@pytest.fixture()
def client() -> TestClient:
    settings = DEFCAISettings(tool_policy="audit", hitl_enabled=False)
    app = create_app(settings=settings)
    return TestClient(app)


class TestHealthEndpoints:
    def test_health(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["module"] == "def-cai"

    def test_ready(self, client: TestClient) -> None:
        resp = client.get("/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert data["ready"] is True

    def test_info(self, client: TestClient) -> None:
        resp = client.get("/info")
        assert resp.status_code == 200
        data = resp.json()
        assert data["paper_arxiv"] == "2504.06017"
        assert data["codename"] == "DEF-CAI"


class TestSessionEndpoints:
    def test_run_session(self, client: TestClient) -> None:
        resp = client.post(
            "/sessions/run",
            json={"objective": "test scan", "pattern_name": "red_blue"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["trace_id"]
        assert data["status"] in ("completed", "interrupted")
        assert data["findings_count"] >= 0
        assert data["turns_executed"] > 0

    def test_run_session_single_agent(self, client: TestClient) -> None:
        resp = client.post(
            "/sessions/run",
            json={"objective": "quick test", "agent_name": "red_team"},
        )
        assert resp.status_code == 200
        assert resp.json()["turns_executed"] >= 1


class TestEvalEndpoints:
    def test_list_datasets(self, client: TestClient) -> None:
        resp = client.get("/eval/datasets")
        assert resp.status_code == 200
        data = resp.json()
        assert "cybermetric" in data

    def test_run_eval(self, client: TestClient) -> None:
        resp = client.post(
            "/eval/run",
            json={"benchmark": "cybermetric", "model_backend": "mock"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["run_id"]
        assert data["total_samples"] >= 0


class TestFindingsEndpoints:
    def test_paper_delta(self, client: TestClient) -> None:
        resp = client.get("/findings/paper-delta")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_claims"] > 0
        assert data["full"] >= 1

    def test_paper_delta_markdown(self, client: TestClient) -> None:
        resp = client.get("/findings/paper-delta/markdown")
        assert resp.status_code == 200
        assert "Paper Reproduction Delta" in resp.json()["markdown"]
