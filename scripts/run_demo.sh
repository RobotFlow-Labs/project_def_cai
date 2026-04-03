#!/usr/bin/env bash
# DEF-CAI Demo — Run a safe session against mock targets
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "=== DEF-CAI Demo ==="
echo "Running red_blue session with audit policy..."

source .venv/bin/activate 2>/dev/null || true

uv run python -m anima_def_cai run \
  --objective "Scan mock robot target for security issues" \
  --pattern red_blue \
  --policy audit

echo ""
echo "=== Demo complete ==="
