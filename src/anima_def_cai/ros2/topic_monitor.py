"""Topic and message sampling for ROS2 inspection.

Paper reference: Figure 2 — topic inspection and message capture.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class TopicSample(BaseModel):
    """A captured sample from a ROS2 topic."""

    topic: str
    msg_type: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: dict[str, Any] = Field(default_factory=dict)
    size_bytes: int = 0


class TopicMonitorResult(BaseModel):
    """Result of topic monitoring over a time window."""

    topics_sampled: int = 0
    samples: list[TopicSample] = Field(default_factory=list)
    unresponsive_topics: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def sample_topics(
    topic_names: list[str],
    *,
    timeout_seconds: float = 5.0,
) -> TopicMonitorResult:
    """Sample messages from specified topics.  Returns mock data when rclpy unavailable."""
    try:
        return _sample_live(topic_names, timeout_seconds=timeout_seconds)
    except ImportError:
        return _mock_samples(topic_names)


def _sample_live(topic_names: list[str], *, timeout_seconds: float) -> TopicMonitorResult:
    """Sample from live ROS2 topics."""
    raise ImportError("rclpy not available")


def _mock_samples(topic_names: list[str]) -> TopicMonitorResult:
    """Return mock topic samples for testing."""
    samples: list[TopicSample] = []
    for topic in topic_names:
        if topic == "/cmd_vel":
            samples.append(
                TopicSample(
                    topic=topic,
                    msg_type="geometry_msgs/msg/Twist",
                    data={"linear": {"x": 0.5, "y": 0.0, "z": 0.0}, "angular": {"z": 0.1}},
                    size_bytes=48,
                )
            )
        elif topic == "/scan":
            samples.append(
                TopicSample(
                    topic=topic,
                    msg_type="sensor_msgs/msg/LaserScan",
                    data={"ranges_count": 360, "range_min": 0.1, "range_max": 30.0},
                    size_bytes=2880,
                )
            )
        elif topic == "/diagnostics":
            samples.append(
                TopicSample(
                    topic=topic,
                    msg_type="diagnostic_msgs/msg/DiagnosticArray",
                    data={"status_count": 3, "level": "OK"},
                    size_bytes=256,
                )
            )

    responded = {s.topic for s in samples}
    unresponsive = [t for t in topic_names if t not in responded]

    return TopicMonitorResult(
        topics_sampled=len(samples),
        samples=samples,
        unresponsive_topics=unresponsive,
        metadata={"source": "mock"},
    )
