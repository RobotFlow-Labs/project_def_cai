# DEF-CAI — ANIMA Module

> **CAI: An Open, Bug Bounty-Ready Cybersecurity AI**
> Paper: [arXiv:2504.06017](https://arxiv.org/abs/2504.06017)

Part of the [ANIMA Intelligence Compiler Suite](https://github.com/RobotFlow-Labs) by AIFLOW LABS LIMITED.

## Domain
Defense

## Status
- [x] Paper verified and local reference repo inspected
- [x] PRD/task suite generated
- [ ] PRD-01 foundation build in progress
- [ ] Runtime orchestration layers
- [ ] Benchmark reproduction harness
- [ ] API + Docker serving
- [ ] ROS2 / robot-security integration

## Quick Start
```bash
cd project_def_cai
uv venv .venv --python python3.11 && uv sync
uv run pytest tests/test_settings.py tests/test_schemas.py -v
```

## License
MIT — AIFLOW LABS LIMITED
