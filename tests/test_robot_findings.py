"""Tests for robot target inspection and safety findings."""

from __future__ import annotations

from anima_def_cai.connectors.robot_targets import (
    RobotEvidenceBundle,
    RobotTargetProfile,
    inspect_robot,
)
from anima_def_cai.ros2.graph_inspector import capture_graph
from anima_def_cai.ros2.safety_checks import analyze
from anima_def_cai.schemas import Severity


class TestSafetyChecks:
    def test_analyze_mock_graph(self) -> None:
        graph = capture_graph()
        result = analyze(graph)
        assert result.total_checks > 0
        assert result.issues_found > 0

    def test_cmd_vel_finding(self) -> None:
        graph = capture_graph()
        result = analyze(graph)
        titles = [f.title for f in result.findings]
        assert "Unprotected velocity command topic" in titles

    def test_sros2_finding(self) -> None:
        graph = capture_graph()
        result = analyze(graph)
        titles = [f.title for f in result.findings]
        assert "SROS2 security not detected" in titles

    def test_exposed_services_finding(self) -> None:
        graph = capture_graph()
        result = analyze(graph)
        titles = [f.title for f in result.findings]
        assert "Sensitive services exposed without authentication" in titles

    def test_severity_levels(self) -> None:
        graph = capture_graph()
        result = analyze(graph)
        severities = {f.severity for f in result.findings}
        assert Severity.HIGH in severities


class TestRobotInspection:
    def test_inspect_default_profile(self) -> None:
        profile = RobotTargetProfile()
        bundle = inspect_robot(profile)
        assert isinstance(bundle, RobotEvidenceBundle)
        assert bundle.graph.node_count > 0
        assert bundle.total_findings > 0

    def test_inspect_with_custom_domain(self) -> None:
        profile = RobotTargetProfile(domain_id=42)
        bundle = inspect_robot(profile)
        assert bundle.graph.domain_id == 42

    def test_evidence_bundle_has_samples(self) -> None:
        profile = RobotTargetProfile()
        bundle = inspect_robot(profile)
        assert bundle.topic_samples.topics_sampled > 0
