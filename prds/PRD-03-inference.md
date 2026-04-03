# PRD-03: Runtime Inference, Tool Execution, and Findings

> Module: DEF-CAI | Priority: P0  
> Depends on: PRD-01, PRD-02  
> Status: ✅ Complete

## Objective
When this PRD is done, DEF-CAI can run a local security session from CLI, invoke safe tool adapters, capture outputs as structured findings, and allow operator interruption through HITL.

## Context (from paper)
The paper shows CAI solving security tasks by alternating reasoning and tool use, including Linux commands, web enumeration, SSH/ROS analysis, and code execution.

**Paper reference**: §2, Fig. 2, Fig. 4  
"Agents execute security actions using Tools for practical tasks..."  
"Through the command-line interface, users can seamlessly interact with agents at any point during execution by simply pressing Ctrl+C."

## Acceptance Criteria
- [x] CLI launches a session with selectable agent or pattern
- [x] Tool adapters cover Linux command execution, code execution, web search, and optional Shodan/SSH/traffic capture
- [x] Findings are emitted as structured markdown+JSON artifacts
- [x] HITL interrupt path pauses execution cleanly and accepts operator instructions
- [x] `uv run pytest tests/test_cli_runtime.py tests/test_tools_linux.py tests/test_findings.py -v` passes

## Files to Create
| File | Purpose | Paper Ref | Est. Lines |
|---|---|---|---|
| `src/anima_def_cai/cli.py` | CLI entrypoint | §2 | ~180 |
| `src/anima_def_cai/runtime/session.py` | Session state manager | §2 | ~180 |
| `src/anima_def_cai/tools/linux.py` | Safe Linux command adapter | Fig. 5 | ~220 |
| `src/anima_def_cai/tools/code.py` | Code execution adapter | Fig. 5 | ~160 |
| `src/anima_def_cai/tools/osint.py` | Search/Shodan adapters | Fig. 5 | ~180 |
| `src/anima_def_cai/tools/network.py` | SSH / traffic adapters | Fig. 2 | ~180 |
| `src/anima_def_cai/reports/findings.py` | Findings formatter | §3.5 | ~140 |
| `tests/test_cli_runtime.py` | CLI session tests | — | ~120 |
| `tests/test_tools_linux.py` | Linux tool tests | — | ~120 |
| `tests/test_findings.py` | Findings/report tests | — | ~80 |

## Architecture Detail (from paper)

### Inputs
- `SessionRequest`: objective, agent/pattern, model backend, env profile
- `ToolInvocation`: tool name, args, policy profile, timeout

### Outputs
- `ToolObservation`: stdout, stderr, exit_code, artifact_paths
- `FindingRecord`: title, severity, evidence, repro_steps, raw_events

### Algorithm
```python
# Paper ReACT-style tool loop
while not state.done:
    action = orchestrator.next_action(state)
    if action.kind == "tool":
        obs = tool_runner.invoke(action.tool_name, action.args)
        state = state.with_observation(obs)
    elif action.kind == "message":
        reporter.emit(action.content)
    elif action.kind == "interrupt":
        state = hitl.pause_and_collect(state)
```

## Dependencies
```toml
typer = ">=0.12"
httpx = ">=0.27"
paramiko = ">=3.5"
```

## Data Requirements
| Asset | Size | Path | Download |
|---|---|---|---|
| Generic Linux tool semantics | 1 file | `repositories/cai/src/cai/tools/reconnaissance/generic_linux_command.py` | DONE |
| Code execution tool semantics | 1 file | `repositories/cai/src/cai/tools/reconnaissance/exec_code.py` | DONE |

## Test Plan
```bash
uv run pytest tests/test_cli_runtime.py tests/test_tools_linux.py tests/test_findings.py -v
```

## References
- Paper: Fig. 2, Fig. 4, §2
- Reference impl: `repositories/cai/src/cai/tools/reconnaissance/generic_linux_command.py`
- Depends on: PRD-01, PRD-02
- Feeds into: PRD-04, PRD-05, PRD-06
