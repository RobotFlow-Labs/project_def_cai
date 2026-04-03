# DEF-CAI — Design & Implementation Checklist

## Paper: CAI: An Open, Bug Bounty-Ready Cybersecurity AI
## ArXiv: 2504.06017
## Repo: https://github.com/aliasrobotics/cai

---

## Phase 1: Scaffold + Verification
- [x] Project structure created
- [ ] Paper PDF downloaded to papers/
- [ ] Paper read and annotated
- [ ] Reference repo cloned
- [ ] Reference demo runs successfully
- [ ] Datasets identified and accessibility confirmed
- [ ] CLAUDE.md filled with paper-specific details
- [ ] PRD.md filled with architecture and plan

## Phase 2: Reproduce
- [ ] Core model implemented in src/anima_def_cai/
- [ ] Training pipeline (scripts/train.py)
- [ ] Evaluation pipeline (scripts/eval.py)
- [ ] Metrics match paper (within ±5%)
- [ ] Dual-compute verified (Mac-first MLX + CUDA server path)

## Phase 3: Adapt to Hardware
- [ ] ZED 2i data pipeline (if applicable)
- [ ] Unitree L2 LiDAR pipeline (if applicable)
- [ ] xArm 6 integration (if manipulation module)
- [ ] Real sensor inference test
- [ ] MLX inference port validated

## Phase 4: ANIMA Integration
- [ ] ROS2 bridge node
- [ ] Docker container builds and runs
- [ ] API endpoints defined
- [ ] Integration test with stack: NIDHOGG

## Shenzhen Demo Readiness
- [ ] Demo script works end-to-end
- [ ] Demo data prepared
- [ ] Demo runs in < 30 seconds
- [ ] Demo visuals are compelling
