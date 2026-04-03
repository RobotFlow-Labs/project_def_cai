# PRD-01: Foundation & Identity Repair

> Module: DEF-CAI | Priority: P0  
> Depends on: None  
> Status: ⬜ Not started

## Objective
When this PRD is done, the repo has a correct `anima_def_cai` package, typed config/schemas, and a reproducible local scaffold aligned to the verified CAI paper rather than the placeholder `DAIKOKUTEN` scaffold.

## Context (from paper)
CAI is introduced as an open, bug bounty-ready cybersecurity AI framework built around modular agents, tools, and human oversight.

**Paper reference**: §2, Fig. 3  
"The framework is constructed around six fundamental pillars that support an integrated system: Agents, Tools, Handoffs, Patterns, Turns, and Human-In-The-Loop (HITL) functionality, with auxiliary elements such as Extensions and Tracing..."

## Acceptance Criteria
- [ ] Package namespace is normalized from `anima_daikokuten` to `anima_def_cai`
- [ ] Settings and config models cover model backend, tool policy, tracing, benchmark, and robotics options
- [ ] Shared schemas exist for agent specs, tool results, turn state, and findings
- [ ] `uv run pytest tests/test_settings.py tests/test_schemas.py -v` passes
- [ ] Repo metadata references the verified CAI paper (`2504.06017`) and not the unrelated `2503.16012`

## Files to Create
| File | Purpose | Paper Ref | Est. Lines |
|---|---|---|---|
| `src/anima_def_cai/__init__.py` | Package root | Fig. 3 | ~20 |
| `src/anima_def_cai/version.py` | Version constant | — | ~10 |
| `src/anima_def_cai/settings.py` | Pydantic settings | §2 | ~140 |
| `src/anima_def_cai/schemas/base.py` | Common schema types | Fig. 3 | ~120 |
| `src/anima_def_cai/schemas/runtime.py` | Turn/action/finding schemas | §2 | ~180 |
| `configs/default.toml` | Default module config | §2 | ~120 |
| `tests/test_settings.py` | Settings tests | — | ~80 |
| `tests/test_schemas.py` | Schema tests | — | ~120 |

## Architecture Detail (from paper)

### Inputs
- `DEFCAISettings`: validated runtime configuration
- `AgentSpec`: name, instructions, tools, backend, safety flags
- `TurnState`: message buffer, current objective, trace id, operator override state

### Outputs
- `FindingRecord`: structured finding with severity, evidence, reproduction text
- `ToolExecutionRecord`: command, duration, stdout/stderr, policy verdict

### Algorithm
```python
# Paper Fig. 3 foundation contracts
class DEFCAISettings(BaseSettings):
    model_backend: str
    tool_policy: str
    tracing_enabled: bool
    benchmark_root: Path
    ros2_enabled: bool


class TurnState(BaseModel):
    objective: str
    messages: list[dict]
    trace_id: str
    interrupted: bool = False
```

## Dependencies
```toml
pydantic = ">=2.10"
pydantic-settings = ">=2.2"
typing-extensions = ">=4.12"
tomli = ">=2.0"
```

## Data Requirements
| Asset | Size | Path | Download |
|---|---|---|---|
| Verified CAI paper PDF | 1 PDF | `papers/2504.06017_CAI-An-Open-Bug-Bounty-Ready-Cybersecurity-AI.pdf` | DONE |
| Reference repo | 1 repo | `repositories/cai/` | DONE |

## Test Plan
```bash
uv run pytest tests/test_settings.py tests/test_schemas.py -v
uv run ruff check src/ tests/
```

## References
- Paper: §2, Fig. 3
- Reference impl: `repositories/cai/src/cai/agents/factory.py`
- Depends on: None
- Feeds into: PRD-02, PRD-03, PRD-04
