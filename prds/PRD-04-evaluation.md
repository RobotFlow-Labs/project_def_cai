# PRD-04: Evaluation & Benchmark Reproduction

> Module: DEF-CAI | Priority: P1  
> Depends on: PRD-01, PRD-02, PRD-03  
> Status: ⬜ Not started

## Objective
When this PRD is done, DEF-CAI can run reproducible CAIBench-style evaluations over public/local assets and emit time, cost, pass, and evidence reports aligned with the paper’s benchmark framing.

## Context (from paper)
The paper’s claims are benchmark-driven: 54 CTF exercises, pass@1/pass100@1, time/cost comparisons, multi-model comparisons, and bug bounty evidence.

**Paper reference**: §3.1-§3.2, Tables 2-4  
"We measure CAI performance using the pass@1 metric..."  
"For CAI... we imposed a maximum limit of 100 interactions... which we denote as pass100@1."

## Acceptance Criteria
- [ ] Evaluation runner supports at least `knowledge`, `privacy`, and `open_ctf_subset` profiles
- [ ] Reports include time, cost, solved count, model, agent/pattern, and artifact links
- [ ] CyberMetric and SecEval can be run from repo-local assets
- [ ] Evaluation config records which paper claims are fully reproduced vs approximated
- [ ] `uv run pytest tests/test_eval_runner.py tests/test_eval_reports.py -v` passes

## Files to Create
| File | Purpose | Paper Ref | Est. Lines |
|---|---|---|---|
| `src/anima_def_cai/eval/runner.py` | Evaluation orchestration | §3.1 | ~220 |
| `src/anima_def_cai/eval/datasets.py` | Dataset registry | §3.1-§3.2 | ~160 |
| `src/anima_def_cai/eval/metrics.py` | Time/cost/pass metrics | Tables 2-4 | ~140 |
| `src/anima_def_cai/reports/eval_report.py` | Markdown/JSON reports | §3 | ~180 |
| `configs/eval/knowledge.toml` | Knowledge benchmark config | §3 | ~80 |
| `configs/eval/privacy.toml` | Privacy benchmark config | §3 | ~60 |
| `configs/eval/open_ctf_subset.toml` | Public subset CTF config | §3.1-§3.2 | ~80 |
| `tests/test_eval_runner.py` | Eval runner tests | — | ~120 |
| `tests/test_eval_reports.py` | Report tests | — | ~100 |

## Architecture Detail (from paper)

### Inputs
- `EvalConfig`: benchmark type, dataset file, model, agent pattern, interaction budget
- `RunTrace`: tool calls, duration, token/cost metadata

### Outputs
- `EvalResult`: solved, elapsed_seconds, usd_cost, pass_metric
- `EvalReport`: markdown summary + machine-readable JSON

### Algorithm
```python
def run_benchmark(cfg: EvalConfig) -> EvalReport:
    for sample in load_dataset(cfg.dataset_file):
        result = session_runner.run(sample.prompt, budget=cfg.interaction_budget)
        metrics.add(result)
    return render_report(metrics.finalize())
```

## Dependencies
```toml
pandas = ">=2.0"
numpy = ">=1.26"
```

## Data Requirements
| Asset | Size | Path | Download |
|---|---|---|---|
| CyberMetric-2-v1 | 1 JSON | `repositories/cai/benchmarks/utils/cybermetric_dataset/CyberMetric-2-v1.json` | DONE |
| SecEval questions | 2 JSON files | `repositories/cai/benchmarks/utils/seceval_dataset/` | DONE |
| CyberPII-Bench | 1 benchmark dir | `repositories/cai/benchmarks/cyberPII-bench/` | DONE |

## Test Plan
```bash
uv run pytest tests/test_eval_runner.py tests/test_eval_reports.py -v
```

## References
- Paper: §3.1-§3.2, Tables 2-4
- Reference impl: `repositories/cai/benchmarks/eval.py`
- Depends on: PRD-01, PRD-02, PRD-03
- Feeds into: PRD-05, PRD-07
