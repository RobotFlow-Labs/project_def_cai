# PRD-06: ROS2 Integration

> Module: DEF-CAI | Priority: P1  
> Depends on: PRD-01, PRD-02, PRD-03  
> Status: ⬜ Not started

## Objective
When this PRD is done, DEF-CAI can inspect ROS2/robotic environments, capture graph/topic/safety evidence, and feed those artifacts into CAI-style red-team, blue-team, and DFIR workflows.

## Context (from paper)
The CAI paper is not limited to generic IT targets; it demonstrates robot cybersecurity workflows and ROS-based forensic analysis.

**Paper reference**: Fig. 2, Table 2, §4  
"CAI performs digital forensics on the robot’s ROS system..."  
"Robotics" appears as a benchmark category where CAI shows strong performance.

## Acceptance Criteria
- [ ] ROS2 node can snapshot node graph, topics, params, and optional rosbag metadata
- [ ] Robot target adapter converts ROS2 artifacts into findings for red/blue/DFIR agents
- [ ] A lab fixture or mocked ROS2 graph is available for tests
- [ ] `uv run pytest tests/test_ros2_graph.py tests/test_robot_findings.py -v` passes
- [ ] Launch instructions exist for a local ROS2 demo target

## Files to Create
| File | Purpose | Paper Ref | Est. Lines |
|---|---|---|---|
| `src/anima_def_cai/ros2/graph_inspector.py` | ROS2 graph capture | Fig. 2 | ~180 |
| `src/anima_def_cai/ros2/topic_monitor.py` | Topic/sample inspection | Fig. 2 | ~160 |
| `src/anima_def_cai/ros2/safety_checks.py` | Safety config anomaly checks | Fig. 2 | ~140 |
| `src/anima_def_cai/connectors/robot_targets.py` | Robot target normalization | §4 | ~140 |
| `configs/ros2/default.toml` | ROS2 integration config | §4 | ~60 |
| `tests/test_ros2_graph.py` | ROS2 graph tests | — | ~100 |
| `tests/test_robot_findings.py` | Robot finding tests | — | ~100 |

## Architecture Detail (from paper)

### Inputs
- `ROSGraphSnapshot`: nodes, topics, services, params
- `RobotTargetProfile`: host, distro, namespaces, safety files, transport options

### Outputs
- `RobotFinding`: issue type, affected node/topic, evidence, severity
- `RobotEvidenceBundle`: graph JSON, selected messages, safety diff

### Algorithm
```python
def inspect_robot(profile: RobotTargetProfile) -> RobotEvidenceBundle:
    graph = ros2.capture_graph(profile)
    topics = ros2.sample_topics(profile)
    findings = safety_checks.analyze(graph, topics, profile)
    return RobotEvidenceBundle(graph=graph, topics=topics, findings=findings)
```

## Dependencies
```toml
rclpy = ">=3.3"
pyyaml = ">=6.0"
```

## Data Requirements
| Asset | Size | Path | Download |
|---|---|---|---|
| Robot/ROS case-study semantics | Paper figures | `papers/2504.06017_CAI-An-Open-Bug-Bounty-Ready-Cybersecurity-AI.pdf` | DONE |
| Local robot lab target | 1 lab environment | User-provided ROS2 environment | NEEDED FOR FULL VALIDATION |

## Test Plan
```bash
uv run pytest tests/test_ros2_graph.py tests/test_robot_findings.py -v
```

## References
- Paper: Fig. 2, Table 2, §4
- Reference signal: CAI robotics benchmark references and ROS citations in paper bibliography
- Depends on: PRD-01, PRD-02, PRD-03
- Feeds into: PRD-07
