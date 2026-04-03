#!/usr/bin/env python3
"""DEF-CAI asset verification — checks all benchmark datasets are present and loadable."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_ASSETS = {
    "CyberMetric-2-v1": (
        PROJECT_ROOT / "repositories/cai/benchmarks/utils/cybermetric_dataset/CyberMetric-2-v1.json"
    ),
    "SecEval questions": (
        PROJECT_ROOT / "repositories/cai/benchmarks/utils/seceval_dataset/questions.json"
    ),
    "SecEval questions-2": (
        PROJECT_ROOT / "repositories/cai/benchmarks/utils/seceval_dataset/questions-2.json"
    ),
    "CTI-Bench MCQ1": (
        PROJECT_ROOT / "repositories/cai/benchmarks/utils/cti_bench_dataset/cti-mcq1.tsv"
    ),
    "CTI-Bench RCM2": (
        PROJECT_ROOT / "repositories/cai/benchmarks/utils/cti_bench_dataset/cti-rcm2.tsv"
    ),
    "CTI-Bench ATE2": (
        PROJECT_ROOT / "repositories/cai/benchmarks/utils/cti_bench_dataset/cti-ate2.tsv"
    ),
    "CTI-Bench VSP2": (
        PROJECT_ROOT / "repositories/cai/benchmarks/utils/cti_bench_dataset/cti-vsp2.tsv"
    ),
    "CyberPII-Bench": (
        PROJECT_ROOT / "repositories/cai/benchmarks/cyberPII-bench/memory01_gold.csv"
    ),
    "Paper PDF": (
        PROJECT_ROOT
        / "papers/2504.06017_CAI-An-Open-Bug-Bounty-Ready-Cybersecurity-AI.pdf"
    ),
}


def check_assets() -> bool:
    print("=" * 60)
    print("DEF-CAI Asset Verification")
    print("=" * 60)

    all_ok = True
    for name, path in REQUIRED_ASSETS.items():
        if path.exists():
            size = path.stat().st_size
            if size == 0:
                print(f"[EMPTY]   {name} — {path} (0 bytes)")
                all_ok = False
            else:
                size_str = f"{size / 1024:.1f}KB" if size < 1_048_576 else f"{size / 1_048_576:.1f}MB"
                print(f"[OK]      {name} — {size_str}")
        else:
            print(f"[MISSING] {name} — {path}")
            all_ok = False

    print()

    # Try loading datasets through the registry
    try:
        from anima_def_cai.eval.datasets import list_datasets

        info = list_datasets(project_root=PROJECT_ROOT)
        total_available = sum(d["files_available"] for d in info.values())
        total_registered = sum(d["files_registered"] for d in info.values())
        print(f"Dataset registry: {total_available}/{total_registered} files available")
        for bench, detail in info.items():
            status = "OK" if detail["files_available"] == detail["files_registered"] else "PARTIAL"
            print(f"  [{status}] {bench}: {detail['files_available']}/{detail['files_registered']}")
    except Exception as e:
        print(f"[WARN] Could not load dataset registry: {e}")

    print()
    if all_ok:
        print("VERDICT: ALL ASSETS READY")
    else:
        print("VERDICT: SOME ASSETS MISSING — check paths above")
    print("=" * 60)
    return all_ok


if __name__ == "__main__":
    sys.exit(0 if check_assets() else 1)
