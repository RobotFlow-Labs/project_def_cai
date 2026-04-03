"""Robot target normalization and evidence bundling.

Converts ROS2 inspection artifacts into CAI-style findings suitable
for red-team, blue-team, and DFIR agent workflows.

Paper reference: Section 4 — robot security case studies.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from anima_def_cai.ros2.graph_inspector import ROSGraphSnapshot, capture_graph
from anima_def_cai.ros2.safety_checks import SafetyCheckResult, analyze
from anima_def_cai.ros2.topic_monitor import TopicMonitorResult, sample_topics
from anima_def_cai.schemas import FindingRecord


class RobotTargetProfile(BaseModel):
    """Configuration for a robot inspection target."""

    host: str = "localhost"
    domain_id: int = 0
    namespaces: list[str] = Field(default_factory=lambda: ["/"])
    transport: str = "udp"
    sros2_enabled: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class RobotEvidenceBundle(BaseModel):
    """Complete evidence bundle from robot inspection."""

    profile: RobotTargetProfile
    graph: ROSGraphSnapshot
    topic_samples: TopicMonitorResult
    safety: SafetyCheckResult
    findings: list[FindingRecord] = Field(default_factory=list)

    @property
    def total_findings(self) -> int:
        return len(self.findings)


def inspect_robot(profile: RobotTargetProfile) -> RobotEvidenceBundle:
    """Run full robot inspection: graph capture, topic sampling, safety analysis."""
    graph = capture_graph(domain_id=profile.domain_id)

    topic_names = [t.name for t in graph.topics]
    topic_samples = sample_topics(topic_names)

    safety = analyze(graph)

    return RobotEvidenceBundle(
        profile=profile,
        graph=graph,
        topic_samples=topic_samples,
        safety=safety,
        findings=list(safety.findings),
    )
