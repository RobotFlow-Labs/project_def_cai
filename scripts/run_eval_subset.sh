#!/usr/bin/env bash
# DEF-CAI Eval — Run CyberMetric knowledge benchmark (dry-run with mock solver)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "=== DEF-CAI Evaluation Subset ==="
echo "Running CyberMetric knowledge benchmark..."

source .venv/bin/activate 2>/dev/null || true

uv run python -c "
from anima_def_cai.eval.runner import EvalConfig, run_benchmark
from anima_def_cai.reports.eval_report import render_eval_markdown

cfg = EvalConfig.from_toml('configs/eval/knowledge.toml')
report = run_benchmark(cfg)
print(render_eval_markdown(report))
print('Paper delta:')
from anima_def_cai.eval.paper_delta import render_paper_delta_markdown
print(render_paper_delta_markdown())
"

echo ""
echo "=== Evaluation complete ==="
