"""Tests for session tracing."""

from __future__ import annotations

from pathlib import Path

from anima_def_cai.telemetry.tracing import TraceBundle, TraceEvent, Tracer


class TestTraceEvent:
    def test_create_event(self) -> None:
        event = TraceEvent(event_type="turn", agent="red_team")
        assert event.event_id
        assert event.event_type == "turn"
        assert event.timestamp


class TestTracer:
    def test_record_events(self) -> None:
        tracer = Tracer(session_id="test-session")
        tracer.record("turn", agent="red_team", duration_seconds=1.5)
        tracer.record("tool_call", agent="red_team", tool="nmap", duration_seconds=5.0)
        tracer.record("finding", agent="red_team", detail={"title": "open port"})

        assert tracer.bundle.event_count == 3
        assert tracer.bundle.session_id == "test-session"

    def test_cost_tracking(self) -> None:
        tracer = Tracer()
        tracer.record("turn", usd_cost=0.01, tokens_used=500)
        tracer.record("turn", usd_cost=0.02, tokens_used=1000)

        assert tracer.bundle.total_cost == 0.03
        assert tracer.bundle.event_count == 2

    def test_duration_tracking(self) -> None:
        tracer = Tracer()
        tracer.record("turn", duration_seconds=2.0)
        tracer.record("tool_call", duration_seconds=3.0)

        assert tracer.bundle.total_duration == 5.0

    def test_save_to_disk(self, tmp_path: Path) -> None:
        tracer = Tracer(session_id="save-test")
        tracer.record("turn", agent="blue_team")
        path = tracer.save(tmp_path)
        assert path.exists()
        assert path.name == "trace_save-test.json"
        content = path.read_text()
        assert "blue_team" in content


class TestTraceBundle:
    def test_empty_bundle(self) -> None:
        bundle = TraceBundle()
        assert bundle.event_count == 0
        assert bundle.total_cost == 0.0
        assert bundle.total_duration == 0.0
