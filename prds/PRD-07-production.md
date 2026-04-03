# PRD-07: Production Hardening & Release

> Module: DEF-CAI | Priority: P2  
> Depends on: PRD-01, PRD-02, PRD-03, PRD-04, PRD-05, PRD-06  
> Status: ⬜ Not started

## Objective
When this PRD is done, DEF-CAI has safety guardrails, tracing, release packaging, demo scripts, and production validation suitable for ANIMA integration and controlled deployment.

## Context (from paper)
The paper repeatedly argues for semi-autonomous operation, human oversight, and responsible security testing. It also highlights prompt-injection and unsafe-command risks in the broader CAI research line.

**Paper reference**: §2, §4  
"Effective security operations still require human teleoperation..."  
"Human-In-The-Loop (HITL) module is therefore not merely a feature but a critical cornerstone..."

## Acceptance Criteria
- [ ] Input/output guardrails block prompt-injection and dangerous command patterns
- [ ] Tracing records turns, tool invocations, costs, and interruptions
- [ ] Release package includes example configs, demo scripts, and operational docs
- [ ] Production validation checklist covers safe lab-only execution and evidence retention
- [ ] `uv run pytest tests/test_guardrails.py tests/test_tracing.py -v` passes

## Files to Create
| File | Purpose | Paper Ref | Est. Lines |
|---|---|---|---|
| `src/anima_def_cai/safety/guardrails.py` | Input/output safety checks | §2 | ~220 |
| `src/anima_def_cai/safety/policy.py` | Policy profiles | §2, §4 | ~120 |
| `src/anima_def_cai/telemetry/tracing.py` | Trace collection | Fig. 3 | ~180 |
| `scripts/run_demo.sh` | Demo launcher | §3-§4 | ~60 |
| `scripts/run_eval_subset.sh` | Repro eval launcher | §3 | ~60 |
| `README.md` | User-facing module guide | — | ~160 |
| `tests/test_guardrails.py` | Guardrail tests | — | ~120 |
| `tests/test_tracing.py` | Tracing tests | — | ~100 |

## Architecture Detail (from paper)

### Inputs
- `SafetyPolicy`: allowed tools, blocked patterns, target profile, operator confirmation rules
- `TraceEvent`: turn id, tool, duration, token/cost metadata, verdict

### Outputs
- `GuardrailDecision`: allow, warn, block, escalate
- `TraceBundle`: session timeline, findings, cost summary, artifacts

### Algorithm
```python
def guarded_tool_call(invocation: ToolInvocation) -> ToolObservation:
    decision = guardrails.check(invocation)
    if decision.blocked:
        return ToolObservation.blocked(decision.reason)
    obs = tool_runner.invoke(invocation)
    tracer.record(invocation, obs, decision)
    return obs
```

## Dependencies
```toml
orjson = ">=3.10"
```

## Data Requirements
| Asset | Size | Path | Download |
|---|---|---|---|
| Guardrail reference behavior | 1 module | `repositories/cai/src/cai/agents/guardrails.py` | DONE |
| Tracing reference behavior | tracing package | `repositories/cai/src/cai/sdk/agents/tracing/` | DONE |

## Test Plan
```bash
uv run pytest tests/test_guardrails.py tests/test_tracing.py -v
```

## References
- Paper: §2, §4
- Reference impl: `repositories/cai/src/cai/agents/guardrails.py`
- Depends on: PRD-01..PRD-06
- Feeds into: final module delivery
