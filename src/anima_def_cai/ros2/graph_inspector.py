"""ROS2 graph capture and inspection.

Captures node graph, topics, services, and parameters from a running
ROS2 system.  Falls back to a mock graph when rclpy is unavailable,
enabling tests and offline development.

Paper reference: Figure 2, Section 4 — robot forensics on ROS systems.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class NodeInfo(BaseModel):
    name: str
    namespace: str = "/"
    publishers: list[str] = Field(default_factory=list)
    subscribers: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)


class TopicInfo(BaseModel):
    name: str
    msg_type: str = ""
    publishers: list[str] = Field(default_factory=list)
    subscribers: list[str] = Field(default_factory=list)


class ROSGraphSnapshot(BaseModel):
    """Complete snapshot of a ROS2 computation graph."""

    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    domain_id: int = 0
    nodes: list[NodeInfo] = Field(default_factory=list)
    topics: list[TopicInfo] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def topic_count(self) -> int:
        return len(self.topics)


def capture_graph(domain_id: int = 0) -> ROSGraphSnapshot:
    """Capture the live ROS2 graph.  Falls back to mock if rclpy unavailable."""
    try:
        return _capture_live(domain_id)
    except ImportError:
        return _mock_graph(domain_id)


def _capture_live(domain_id: int) -> ROSGraphSnapshot:
    """Capture from a live ROS2 system using rclpy."""
    import rclpy  # type: ignore[import-untyped]
    from rclpy.node import Node  # type: ignore[import-untyped]

    rclpy.init(domain_id=domain_id)
    inspector = Node("def_cai_inspector")
    try:
        node_names = inspector.get_node_names_and_namespaces()
        nodes: list[NodeInfo] = []
        for name, ns in node_names:
            pubs = [t for t, _ in inspector.get_publisher_names_and_types_by_node(name, ns)]
            subs = [t for t, _ in inspector.get_subscriber_names_and_types_by_node(name, ns)]
            srvs = [s for s, _ in inspector.get_service_names_and_types_by_node(name, ns)]
            nodes.append(
                NodeInfo(name=name, namespace=ns, publishers=pubs, subscribers=subs, services=srvs)
            )

        topic_list = inspector.get_topic_names_and_types()
        topics = [TopicInfo(name=t, msg_type=types[0] if types else "") for t, types in topic_list]

        return ROSGraphSnapshot(domain_id=domain_id, nodes=nodes, topics=topics)
    finally:
        inspector.destroy_node()
        rclpy.shutdown()


def _mock_graph(domain_id: int = 0) -> ROSGraphSnapshot:
    """Return a representative mock graph for testing without ROS2."""
    return ROSGraphSnapshot(
        domain_id=domain_id,
        nodes=[
            NodeInfo(
                name="robot_driver",
                namespace="/mir",
                publishers=["/cmd_vel", "/diagnostics"],
                subscribers=["/scan", "/odom"],
                services=["/set_mode"],
            ),
            NodeInfo(
                name="navigation",
                namespace="/mir",
                publishers=["/cmd_vel"],
                subscribers=["/scan", "/map", "/odom"],
                services=["/navigate_to"],
            ),
            NodeInfo(
                name="safety_monitor",
                namespace="/mir",
                publishers=["/diagnostics", "/safety_status"],
                subscribers=["/scan", "/cmd_vel"],
            ),
        ],
        topics=[
            TopicInfo(name="/cmd_vel", msg_type="geometry_msgs/msg/Twist"),
            TopicInfo(name="/scan", msg_type="sensor_msgs/msg/LaserScan"),
            TopicInfo(name="/odom", msg_type="nav_msgs/msg/Odometry"),
            TopicInfo(name="/diagnostics", msg_type="diagnostic_msgs/msg/DiagnosticArray"),
            TopicInfo(name="/safety_status", msg_type="std_msgs/msg/Bool"),
        ],
        metadata={"source": "mock", "note": "rclpy not available — using mock graph"},
    )
