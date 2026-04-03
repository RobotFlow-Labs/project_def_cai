"""Safety configuration anomaly checks for ROS2 robot systems.

Analyses a captured ROS2 graph for common security misconfigurations
found in robot deployments (unencrypted topics, missing auth, exposed
services).

Paper reference: Figure 2, Section 4 — demonstrated vulnerabilities in MIR robots.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from anima_def_cai.ros2.graph_inspector import ROSGraphSnapshot
from anima_def_cai.schemas import FindingRecord, Severity, FindingKind


class SafetyCheckResult(BaseModel):
    """Aggregated results from ROS2 safety analysis."""

    total_checks: int = 0
    issues_found: int = 0
    findings: list[FindingRecord] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def analyze(graph: ROSGraphSnapshot) -> SafetyCheckResult:
    """Run all safety checks against a graph snapshot."""
    findings: list[FindingRecord] = []
    checks = 0

    # Check 1: Unencrypted cmd_vel topic (critical for mobile robots)
    checks += 1
    cmd_vel_topics = [t for t in graph.topics if "cmd_vel" in t.name]
    if cmd_vel_topics:
        findings.append(
            FindingRecord(
                title="Unprotected velocity command topic",
                summary=(
                    f"Topic {cmd_vel_topics[0].name} accepts velocity commands "
                    "without SROS2 encryption or access control."
                ),
                severity=Severity.HIGH,
                kind=FindingKind.VULNERABILITY,
                evidence=[f"topic={cmd_vel_topics[0].name}", f"type={cmd_vel_topics[0].msg_type}"],
                confidence=0.85,
            )
        )

    # Check 2: No SROS2 security directory detected
    checks += 1
    has_security = any("security" in str(n.parameters) for n in graph.nodes)
    if not has_security:
        findings.append(
            FindingRecord(
                title="SROS2 security not detected",
                summary="No SROS2 security configuration found in node parameters.",
                severity=Severity.MEDIUM,
                kind=FindingKind.MISCONFIGURATION,
                evidence=["No security-related parameters in any node"],
                confidence=0.7,
            )
        )

    # Check 3: Exposed services without authentication
    checks += 1
    exposed_services = []
    for node in graph.nodes:
        for srv in node.services:
            if any(kw in srv for kw in ("set_mode", "navigate", "shutdown", "restart")):
                exposed_services.append(f"{node.namespace}/{node.name}: {srv}")
    if exposed_services:
        findings.append(
            FindingRecord(
                title="Sensitive services exposed without authentication",
                summary=f"{len(exposed_services)} sensitive service(s) accessible without auth.",
                severity=Severity.HIGH,
                kind=FindingKind.VULNERABILITY,
                evidence=exposed_services,
                confidence=0.8,
            )
        )

    # Check 4: Diagnostic data broadcast
    checks += 1
    diag_topics = [t for t in graph.topics if "diagnostic" in t.name]
    if diag_topics:
        findings.append(
            FindingRecord(
                title="Diagnostic data broadcast on open topic",
                summary="Diagnostic information published without access control.",
                severity=Severity.LOW,
                kind=FindingKind.OBSERVATION,
                evidence=[f"topic={t.name}" for t in diag_topics],
                confidence=0.6,
            )
        )

    return SafetyCheckResult(
        total_checks=checks,
        issues_found=len(findings),
        findings=findings,
        metadata={"graph_nodes": graph.node_count, "graph_topics": graph.topic_count},
    )
