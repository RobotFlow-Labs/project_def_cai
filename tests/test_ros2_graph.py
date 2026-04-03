"""Tests for ROS2 graph inspection and topic monitoring."""

from __future__ import annotations

from anima_def_cai.ros2.graph_inspector import ROSGraphSnapshot, capture_graph
from anima_def_cai.ros2.topic_monitor import sample_topics


class TestGraphCapture:
    def test_mock_graph_returns_snapshot(self) -> None:
        graph = capture_graph(domain_id=42)
        assert isinstance(graph, ROSGraphSnapshot)
        assert graph.node_count > 0
        assert graph.topic_count > 0

    def test_mock_graph_has_mir_nodes(self) -> None:
        graph = capture_graph()
        names = [n.name for n in graph.nodes]
        assert "robot_driver" in names
        assert "navigation" in names
        assert "safety_monitor" in names

    def test_mock_graph_has_expected_topics(self) -> None:
        graph = capture_graph()
        topic_names = [t.name for t in graph.topics]
        assert "/cmd_vel" in topic_names
        assert "/scan" in topic_names

    def test_mock_graph_metadata(self) -> None:
        graph = capture_graph()
        assert graph.metadata.get("source") == "mock"


class TestTopicMonitor:
    def test_sample_known_topics(self) -> None:
        result = sample_topics(["/cmd_vel", "/scan", "/diagnostics"])
        assert result.topics_sampled == 3
        assert len(result.samples) == 3

    def test_unresponsive_topic(self) -> None:
        result = sample_topics(["/nonexistent_topic"])
        assert result.topics_sampled == 0
        assert "/nonexistent_topic" in result.unresponsive_topics

    def test_sample_data_structure(self) -> None:
        result = sample_topics(["/cmd_vel"])
        assert result.samples[0].topic == "/cmd_vel"
        assert result.samples[0].msg_type == "geometry_msgs/msg/Twist"
        assert result.samples[0].size_bytes > 0
