# PRD-05: API & Docker

> Module: DEF-CAI | Priority: P1  
> Depends on: PRD-01, PRD-02, PRD-03, PRD-04  
> Status: ⬜ Not started

## Objective
When this PRD is done, DEF-CAI exposes its runtime and evaluation flows through a containerized FastAPI service suitable for local lab orchestration and ANIMA composition.

## Context (from paper)
The paper emphasizes accessibility, reproducibility, and practical deployment. The CAI repo already ships Dockerized assets and a CLI-first workflow.

**Paper reference**: §1, §2  
"CAI provides the building blocks to create specialized AI agents..."  
"By combining modular agent design with seamless tool integration and human oversight..."

## Acceptance Criteria
- [ ] FastAPI exposes health, session run, eval run, and findings retrieval endpoints
- [ ] Dockerfile and compose setup boot the API with a documented env contract
- [ ] API can run a safe dry-run session without external credentials
- [ ] `uv run pytest tests/test_api.py -v` passes
- [ ] `docker compose up` for DEF-CAI succeeds locally

## Files to Create
| File | Purpose | Paper Ref | Est. Lines |
|---|---|---|---|
| `src/anima_def_cai/api/app.py` | FastAPI app | §1-§2 | ~180 |
| `src/anima_def_cai/api/routes/session.py` | Session endpoints | §2 | ~140 |
| `src/anima_def_cai/api/routes/eval.py` | Eval endpoints | §3 | ~120 |
| `src/anima_def_cai/api/routes/findings.py` | Findings/report endpoints | §3.5 | ~100 |
| `docker/Dockerfile` | Container image | — | ~60 |
| `docker/docker-compose.yml` | Local orchestration | — | ~60 |
| `.env.example` | API/backend env contract | — | ~80 |
| `tests/test_api.py` | API tests | — | ~120 |

## Architecture Detail (from paper)

### Inputs
- `POST /sessions/run`: objective, agent, target profile, tool policy
- `POST /eval/run`: benchmark, dataset path, model, interaction budget

### Outputs
- `SessionResponse`: trace id, status, findings count, latest message
- `EvalResponse`: report path, solved count, elapsed seconds, usd cost

### Algorithm
```python
@router.post("/sessions/run")
def run_session(req: SessionRequest) -> SessionResponse:
    state = session_service.start(req)
    summary = session_service.execute(state)
    return SessionResponse.from_summary(summary)
```

## Dependencies
```toml
fastapi = ">=0.111"
uvicorn = ">=0.30"
python-multipart = ">=0.0.9"
```

## Data Requirements
| Asset | Size | Path | Download |
|---|---|---|---|
| CAI docker reference | 1 Docker setup | `repositories/cai/dockerized/` | DONE |

## Test Plan
```bash
uv run pytest tests/test_api.py -v
docker compose -f docker/docker-compose.yml config
```

## References
- Paper: §1-§2
- Reference impl: `repositories/cai/dockerized/Dockerfile`
- Depends on: PRD-01, PRD-02, PRD-03, PRD-04
- Feeds into: PRD-07
