# DEF-CAI: CAI — Implementation PRD
## ANIMA Wave-7 Module

**Status:** PRD Suite Generated  
**Version:** 0.2  
**Date:** 2026-04-03  
**Module:** DEF-CAI  
**Verified Paper:** CAI: An Open, Bug Bounty-Ready Cybersecurity AI  
**Verified Paper Link:** https://arxiv.org/abs/2504.06017  
**Reference Repo:** https://github.com/aliasrobotics/cai  
**Functional Name:** `def-cai`  
**Stack:** ANIMA Intelligence Compiler Suite

## 1. Executive Summary
DEF-CAI will reproduce the CAI framework as an ANIMA-native cybersecurity orchestration module focused on agent coordination, safe tool execution, benchmark reproduction, and robot-security integration. The implementation target is not a neural model but a faithful rebuild of the paper’s agent/tool/handoff/pattern/HITL architecture, benchmark flows, and robot-focused case-study workflows.

## 2. Paper Verification Status
- [x] Local project paper path inspected
- [x] Local PDF mismatch detected and rejected (`2503.16012` is unrelated)
- [x] Correct CAI paper downloaded and read (`2504.06017`)
- [x] GitHub reference repo inspected in `repositories/cai`
- [x] Local benchmark assets identified in `repositories/cai/benchmarks`
- [x] Core architecture, benchmark claims, and bug bounty evidence extracted
- [ ] Exact private competition assets available locally
- [ ] Exact private bug bounty targets available locally
- **Verdict:** VERIFIED FOR FRAMEWORK REPRODUCTION, PARTIAL FOR EXACT PRIVATE-ASSET REPLICATION

## 3. What We Take From The Paper
- The agent-centric CAI architecture centered on Agents, Tools, Handoffs, Patterns, Turns, HITL, plus Tracing and Guardrails.
- The specialized red-team, bug-bounty, and blue-team operating modes shown in Figure 5.
- The Kali-Linux-rootfs execution assumption and command-driven workflow.
- The CAIBench evaluation framing, including CTF, knowledge, privacy, and robotics-oriented benchmarks.
- The robotics security angle demonstrated through MIR/ROS/MQTT-style case studies.
- The strong requirement for human oversight over fully autonomous operation.

## 4. What We Skip
- Any attempt to reproduce private Hack The Box competition infrastructure exactly.
- Any attempt to replay private bug bounty submissions against undisclosed real targets.
- Unrelated agents and commercial-only CAI PRO features not necessary to match the paper’s public core.
- Placeholder ML dependencies from the current scaffold that do not belong to a framework reproduction.

## 5. What We Adapt
- We adapt CAI’s generic framework into an ANIMA module layout under `src/anima_def_cai/`.
- We add explicit ROS2 integration as an ANIMA-facing robotics bridge, justified by the paper’s robot-security case studies and cited ROS/SROS2 work.
- We define reproducible open benchmark subsets from the repo-local assets where the paper used private or competition-only data.
- We formalize configuration, schemas, tests, and Docker/API packaging to match ANIMA build conventions.

## 6. Architecture

### Runtime Flow
1. User or CI triggers a run from CLI or API.
2. A Pattern selects or composes one or more Agents.
3. Agents reason over state using an LLM backend.
4. Agents invoke controlled Tools for Linux, web, code, SSH, OSINT, or traffic analysis.
5. Handoffs route work to specialized agents when required.
6. Guardrails validate inbound context and outbound commands.
7. Tracing records actions and decisions.
8. Evaluation/reporting converts outputs into benchmark and bug-finding artifacts.

### Core Interfaces
- `AgentSpec`: instructions, tool bindings, backend settings, safety hooks
- `ToolResult`: command output, artifacts, execution metadata, policy outcome
- `TurnState`: messages, findings, actions, interruptions, trace ids
- `PatternPlan`: ordered or parallel execution graph across agents
- `EvaluationRecord`: benchmark id, outcome, time, cost, evidence

### Initial Module Layout Target
```text
src/anima_def_cai/
├── cli.py
├── settings.py
├── schemas/
├── core/
├── runtime/
├── agents/
├── patterns/
├── tools/
├── safety/
├── telemetry/
├── eval/
├── reports/
└── ros2/
```

## 7. Implementation Phases

### Phase 1 — Foundation + Identity Repair
- [ ] Replace `anima_daikokuten` scaffolding references with `anima_def_cai`
- [ ] Establish settings, schemas, package layout, and typed runtime contracts
- [ ] Normalize project metadata around the verified CAI paper

### Phase 2 — Core CAI Runtime
- [ ] Implement agents, patterns, handoffs, turn runtime, and HITL loop
- [ ] Port the minimal tool layer required by the paper’s public workflows
- [ ] Add safety guardrails and tracing hooks

### Phase 3 — Evaluation + Evidence
- [ ] Recreate CAIBench-compatible evaluation flows from public/local assets
- [ ] Produce benchmark and bug-bounty style reports
- [ ] Validate the paper’s published claims directionally on open subsets

### Phase 4 — API, Docker, Robotics
- [ ] Expose runtime through FastAPI and Docker
- [ ] Add ROS2 inspection and robot-target adapters
- [ ] Prepare ANIMA-compatible integration surfaces

### Phase 5 — Production Hardening
- [ ] Harden safety policy, observability, and graceful failure modes
- [ ] Add release packaging and reproducibility docs
- [ ] Prepare demo and ops playbooks

## 8. Datasets / Assets
| Dataset / Asset | Path | Phase Needed |
|---|---|---|
| CyberMetric-2-v1 | `repositories/cai/benchmarks/utils/cybermetric_dataset/CyberMetric-2-v1.json` | Phase 3 |
| SecEval datasets | `repositories/cai/benchmarks/utils/seceval_dataset/` | Phase 3 |
| CTI Bench TSVs | `repositories/cai/benchmarks/utils/cti_bench_dataset/` | Phase 3 |
| CyberPII-Bench | `repositories/cai/benchmarks/cyberPII-bench/` | Phase 3 |
| Competition and private bug bounty assets | Paper only | Phase 3 delta documentation |

## 9. Dependencies on Other Wave Projects
| Needs output from | What it provides |
|---|---|
| None required for initial build | DEF-CAI is self-contained as a framework module |
| Optional future ANIMA orchestration modules | Shared runtime abstractions, ROS2 launch integration, cross-module telemetry |

## 10. Success Criteria
- DEF-CAI reproduces the paper’s architectural pillars with concrete tests and runnable flows.
- The module ships red-team, bug-bounty, blue-team, and DFIR-capable workflows grounded in the reference repo.
- Public/local benchmark subsets run through a reproducible evaluation harness.
- The benchmark layer can report paper-aligned metrics including pass@1/pass100@1, time, and cost.
- Robotics-facing inspection flows support ROS2 graph, topic, and artifact analysis.
- Safety controls block prompt-injection and dangerous command patterns before execution.

## 11. Risk Assessment
| Risk | Impact | Mitigation |
|---|---|---|
| Wrong paper identity in scaffold | Invalid implementation direction | Locked to verified paper + correction notes in all planning docs |
| Private benchmark assets unavailable | Exact paper reproduction impossible | Use public subset reproduction and mark deltas clearly |
| Reference repo scope is broader than paper | Overbuilding | PRDs prioritize figures, tables, and directly cited workflows |
| Existing scaffold package names are wrong | Confusing future implementation | First foundation PRD includes explicit namespace repair |
| Tool misuse in offensive workflows | Safety and policy risk | Guardrails + explicit local-only / lab-only validation rules |

## 12. Build Plan
| PRD# | Task | Status |
|---|---|---|
| [PRD-01](prds/PRD-01-foundation.md) | Foundation, naming repair, config, schemas | ✅ |
| [PRD-02](prds/PRD-02-core-model.md) | Core orchestration model: agents, patterns, handoffs, runtime | ✅ |
| [PRD-03](prds/PRD-03-inference.md) | CLI runtime, tool execution, findings pipeline | ✅ |
| [PRD-04](prds/PRD-04-evaluation.md) | CAIBench-style evaluation and report generation | ✅ |
| [PRD-05](prds/PRD-05-api-docker.md) | FastAPI and Docker packaging | ✅ |
| [PRD-06](prds/PRD-06-ros2-integration.md) | ROS2 / robot-security integration | ✅ |
| [PRD-07](prds/PRD-07-production.md) | Hardening, release, observability, production validation | ⬜ |

## 13. Near-Term Demo Target
- **Demo-ready target:** Phase 3 minimum
- **Demo scenario:** Launch DEF-CAI locally, run a bug-bounty or red-team workflow against a safe lab target, record findings, and show a ROS2/robot-target inspection pass
- **Evidence bundle:** benchmark JSON, markdown report, trace log, CLI transcript, Docker run instructions
