# DEF-CAI — Asset Manifest

## Paper
- Title: CAI: An Open, Bug Bounty-Ready Cybersecurity AI
- Requested project reference: `2503.16012` in scaffold docs
- Verified implementation paper used for this PRD suite: `2504.06017`
- Authors: Victor Mayoral-Vilches et al.
- Source PDF: `papers/2504.06017_CAI-An-Open-Bug-Bounty-Ready-Cybersecurity-AI.pdf`
- Local mismatch note: `papers/2503.16012_CAI-Framework.pdf` is not the CAI paper and should not be used for implementation planning

## Status: READY

## Model Backends / Runtime Dependencies
| Model / Backend | Type | Source | Path | Status |
|---|---|---|---|---|
| `claude-3.7-sonnet-2025-02-19` | Hosted LLM | Anthropic API | Remote API | PAPER-VERIFIED |
| `o3-mini-2025-01-31` | Hosted LLM | OpenAI API | Remote API | PAPER-VERIFIED |
| `gpt-4o-2024-11-20` | Hosted LLM | OpenAI API | Remote API | PAPER-VERIFIED |
| `gemini-2.5-pro-exp-03-25` | Hosted LLM | Google API | Remote API | PAPER-VERIFIED |
| `deepseek-v3-2024-12-26` | Hosted LLM | DeepSeek API | Remote API | PAPER-VERIFIED |
| `qwen2.5:14b` | Open-weight LLM | Qwen/Ollama runtime | External runtime | OPTIONAL |
| `qwen2.5:72b` | Open-weight LLM | Qwen/Ollama runtime | External runtime | OPTIONAL |
| `alias1` | Alias Robotics CAI model alias | Alias Robotics runtime | Remote API | REPO-VERIFIED |

## Datasets / Benchmark Assets
| Dataset / Asset | Size / Count | Split / Scope | Source | Path | Status |
|---|---|---|---|---|---|
| CAIBench challenge corpus | 54 CTF exercises | Multi-category | Paper Appendix B / CAI repo | `repositories/cai/benchmarks/README.md` | PAPER-VERIFIED |
| 23-CTF LLM comparison subset | 23 challenges | LLM benchmark subset | Paper §3.2 | Paper only | PAPER-VERIFIED |
| CyberMetric-2-v1 | JSON benchmark | Knowledge benchmark | CAI repo | `repositories/cai/benchmarks/utils/cybermetric_dataset/CyberMetric-2-v1.json` | READY-LOCAL |
| SecEval questions | JSON benchmark | Knowledge benchmark | CAI repo | `repositories/cai/benchmarks/utils/seceval_dataset/questions.json` | READY-LOCAL |
| SecEval questions-2 | JSON benchmark | Knowledge benchmark | CAI repo | `repositories/cai/benchmarks/utils/seceval_dataset/questions-2.json` | READY-LOCAL |
| CTI Bench TSVs | TSV benchmark | Knowledge benchmark | CAI repo | `repositories/cai/benchmarks/utils/cti_bench_dataset/` | READY-LOCAL |
| CyberPII-Bench | CSV/privacy benchmark | Privacy benchmark | CAI repo | `repositories/cai/benchmarks/cyberPII-bench/` | READY-LOCAL |
| HTB / live-CTF measurements | Private competition results | Benchmark evidence | Paper §3.3-§3.4 | Paper only | PAPER-ONLY |
| Bug bounty exercise results | 1-week exercises | Non-pro + pro findings | Paper §3.5 | Paper only | PAPER-ONLY |
| Robotics case-study targets | MIR / ROS / MQTT style targets | Demo / validation | Paper Fig. 2, §4 | Not bundled | NEEDS-LOCAL-LAB |

## Hyperparameters / Run Parameters (Paper-Derived)
| Param | Value | Paper Section |
|---|---|---|
| evaluation_metric | `pass@1` | §3.1 |
| interaction_budget | `pass100@1` with max 100 LLM interactions | §3.1 |
| execution_environment | Kali Linux (Rolling) root filesystem | §3.1, §3.2 |
| human_cost_rate | EUR 45/hour (USD 48.54/hour used in tables) | Table 2 note |
| default_best_pattern | Red Team Agent pattern for most CTFs | §3.1 |
| minimal_llm_pattern | `one_tool_agent` + one Linux command tool | §3.2 |
| bug_bounty_window | 1 week | §3.5 |
| bug_bounty_pattern | Bug Bounty Agent | §3.5 |

## Expected Metrics (Paper-Derived Targets)
| Benchmark | Metric | Paper Value | Our Target |
|---|---|---|---|
| CAI vs humans overall CTF categories | Time ratio | `11x` faster | `>= 8x` on reproduced local subset |
| CAI vs humans overall CTF categories | Cost ratio | `156x` lower cost | `>= 100x` on reproduced local subset |
| Forensics category | Time ratio | `938x` | Match directionally on local subset |
| Robotics category | Time ratio | `741x` | Match directionally on robotics subset |
| Reverse engineering category | Time ratio | `774x` | Match directionally on local subset |
| Claude 3.7 on 23-CTF subset | Solved challenges | `19 / 23` | `>= 17 / 23` if same subset is rebuilt |
| Live HTB AI vs Human CTF | Rank | `1st` among AI teams, top-20 overall | Documented reproduction/demo only |
| Bug bounty exercise (non-pro) | Valid findings | 6 findings listed incl. CVE-2021-3618 | Reproduce workflow, not private findings |

## Reference Implementation
| Asset | Source | Path | Status |
|---|---|---|---|
| CAI framework repo | Alias Robotics | `repositories/cai/` | READY-LOCAL |
| Primary architecture doc | CAI repo docs | `repositories/cai/docs/cai_architecture.md` | READY-LOCAL |
| Benchmark doc | CAI repo docs | `repositories/cai/docs/cai_benchmark.md` | READY-LOCAL |
| Core benchmark runner | CAI repo | `repositories/cai/benchmarks/eval.py` | READY-LOCAL |
| Agent factory | CAI repo | `repositories/cai/src/cai/agents/factory.py` | READY-LOCAL |
| Guardrails module | CAI repo | `repositories/cai/src/cai/agents/guardrails.py` | READY-LOCAL |

## Notes
- This module is a framework/orchestration build, not a neural-network training reproduction.
- The paper is grounded in agent design, tool orchestration, guardrails, benchmarking, and robot-security case studies.
- PRDs therefore target a faithful ANIMA implementation of CAI’s architecture, benchmarks, and robotics hooks instead of inventing an ML pipeline not present in the paper.
