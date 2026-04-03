# DEF-CAI

## Paper
**CAI: Robot Cybersecurity Assessment Framework**
Verified implementation paper: https://arxiv.org/abs/2504.06017
Scaffold note: `2503.16012` in the original placeholder docs was incorrect for CAI

## Module Identity
- Codename: DEF-CAI
- Domain: Defense
- Part of ANIMA Intelligence Compiler Suite

## Structure
```
project_def_cai/
├── pyproject.toml
├── configs/
├── src/anima_def_cai/
├── tests/
├── scripts/
├── papers/          # Paper PDF
├── CLAUDE.md        # This file
├── NEXT_STEPS.md
├── ASSETS.md
└── PRD.md
```

## Commands
```bash
uv sync
uv run pytest
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

## Conventions
- Package manager: uv (never pip)
- Build backend: hatchling
- Python: >=3.10
- Config: TOML + Pydantic BaseSettings
- Lint: ruff
- Git commit prefix: [DEF-CAI]
