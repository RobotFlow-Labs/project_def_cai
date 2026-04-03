# PRD-02: Core Orchestration Model

> Module: DEF-CAI | Priority: P0  
> Depends on: PRD-01  
> Status: ✅ Complete

## Objective
When this PRD is done, DEF-CAI can instantiate specialized agents, coordinate them via patterns and handoffs, and execute multi-turn cybersecurity workflows with typed state transitions.

## Context (from paper)
CAI’s core contribution is its agent-centric architecture and specialized patterns rather than a monolithic model.

**Paper reference**: §2, Fig. 3, Fig. 5  
"At the core of CAI is the concept of specialized cybersecurity agents working together through well-defined interaction patterns."  
"Specialized Cybersecurity Agent Patterns in CAI: Red Team Agent, Bug Bounty Hunter, and Blue Team Agent..."

## Acceptance Criteria
- [x] Agent registry supports at least `red_team`, `bug_bounty`, `blue_team`, `dfir`, and `retester`
- [x] Pattern engine supports sequential and parallel orchestration
- [x] Handoff rules can route from bug bounty to retester / reporter flows
- [x] Turn runtime preserves message history, findings, and interrupts
- [x] `uv run pytest tests/test_agent_registry.py tests/test_patterns.py tests/test_handoffs.py -v` passes

## Files to Create
| File | Purpose | Paper Ref | Est. Lines |
|---|---|---|---|
| `src/anima_def_cai/core/agent_registry.py` | Agent factory/registry | Fig. 3 | ~180 |
| `src/anima_def_cai/core/handoffs.py` | Handoff contracts | Fig. 3 | ~140 |
| `src/anima_def_cai/patterns/base.py` | Pattern abstraction | Fig. 3, Fig. 5 | ~180 |
| `src/anima_def_cai/patterns/red_blue.py` | Red/blue pattern | Fig. 5 | ~120 |
| `src/anima_def_cai/patterns/bug_bounty.py` | Bug bounty workflow | Fig. 5, §3.5 | ~120 |
| `src/anima_def_cai/runtime/turn_engine.py` | Multi-turn runtime | §2 | ~220 |
| `src/anima_def_cai/agents/*.py` | Agent specs and prompts | Fig. 5 | ~300 total |
| `tests/test_agent_registry.py` | Registry tests | — | ~90 |
| `tests/test_patterns.py` | Pattern tests | — | ~120 |
| `tests/test_handoffs.py` | Handoff tests | — | ~80 |

## Architecture Detail (from paper)

### Inputs
- `TurnState.messages: list[dict[str, str]]`
- `PatternPlan.steps: list[PatternStep]`
- `AgentSpec.tools: list[str]`

### Outputs
- `AgentAction`: tool call, handoff, answer, or stop
- `RunSummary`: turns, findings, tool calls, interruptions, duration

### Algorithm
```python
# Paper Fig. 3 / Fig. 5 orchestration
def run_turn(state: TurnState, pattern: PatternPlan) -> RunSummary:
    for step in pattern.iter_steps():
        agent = registry.build(step.agent_name, state)
        action = agent.reason_and_act(state)
        state = apply_action(state, action)
        if action.kind == "handoff":
            state = transfer(state, action.target_agent)
        if state.interrupted:
            break
    return summarize(state)
```

## Dependencies
```toml
openai = ">=1.75"
networkx = ">=3.0"
rich = ">=13.9"
```

## Data Requirements
| Asset | Size | Path | Download |
|---|---|---|---|
| CAI agent definitions | 6+ agent files | `repositories/cai/src/cai/agents/` | DONE |
| CAI pattern definitions | 4+ pattern files | `repositories/cai/src/cai/agents/patterns/` | DONE |

## Test Plan
```bash
uv run pytest tests/test_agent_registry.py tests/test_patterns.py tests/test_handoffs.py -v
```

## References
- Paper: §2, Fig. 3, Fig. 5
- Reference impl: `repositories/cai/src/cai/agents/factory.py`
- Reference impl: `repositories/cai/src/cai/agents/patterns/pattern.py`
- Depends on: PRD-01
- Feeds into: PRD-03, PRD-04, PRD-06
