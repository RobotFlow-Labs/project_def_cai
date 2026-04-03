"""Dataset registry for CAIBench knowledge, privacy, and CTF benchmarks.

Supports CyberMetric, SecEval, CTI-Bench, and CyberPII-Bench from the
reference repo's local assets.  Each loader returns a normalised list of
:class:`BenchmarkSample` objects so that the runner can treat every
dataset uniformly.

Paper reference: Section 3.1-3.2, Tables 2-4.
"""

from __future__ import annotations

import csv
import json
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class BenchmarkType(StrEnum):
    CYBERMETRIC = "cybermetric"
    SECEVAL = "seceval"
    CTI_BENCH = "cti_bench"
    CYBERPII = "cyberpii"
    OPEN_CTF = "open_ctf"


class BenchmarkSample(BaseModel):
    """Normalised benchmark question/challenge."""

    id: str
    benchmark: BenchmarkType
    question: str
    choices: dict[str, str] = Field(default_factory=dict)
    answer: str = ""
    prompt: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Default relative paths (from project root → repositories/cai/benchmarks/)
# ---------------------------------------------------------------------------
_BENCH_ROOT = Path("repositories/cai/benchmarks")

DATASET_PATHS: dict[BenchmarkType, list[Path]] = {
    BenchmarkType.CYBERMETRIC: [
        _BENCH_ROOT / "utils" / "cybermetric_dataset" / "CyberMetric-2-v1.json",
    ],
    BenchmarkType.SECEVAL: [
        _BENCH_ROOT / "utils" / "seceval_dataset" / "questions.json",
        _BENCH_ROOT / "utils" / "seceval_dataset" / "questions-2.json",
    ],
    BenchmarkType.CTI_BENCH: [
        _BENCH_ROOT / "utils" / "cti_bench_dataset" / "cti-mcq1.tsv",
        _BENCH_ROOT / "utils" / "cti_bench_dataset" / "cti-rcm2.tsv",
        _BENCH_ROOT / "utils" / "cti_bench_dataset" / "cti-ate2.tsv",
        _BENCH_ROOT / "utils" / "cti_bench_dataset" / "cti-vsp2.tsv",
    ],
    BenchmarkType.CYBERPII: [
        _BENCH_ROOT / "cyberPII-bench" / "memory01_gold.csv",
    ],
}


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def _load_cybermetric(path: Path) -> list[BenchmarkSample]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    questions = data.get("questions", data if isinstance(data, list) else [])
    samples: list[BenchmarkSample] = []
    for idx, item in enumerate(questions):
        samples.append(
            BenchmarkSample(
                id=f"cybermetric-{idx}",
                benchmark=BenchmarkType.CYBERMETRIC,
                question=item["question"],
                choices=item.get("answers", {}),
                answer=item.get("solution", ""),
                prompt=item["question"],
                metadata={"source_file": path.name},
            )
        )
    return samples


def _load_seceval(path: Path) -> list[BenchmarkSample]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    items = data if isinstance(data, list) else data.get("questions", [])
    samples: list[BenchmarkSample] = []
    for item in items:
        choices_raw = item.get("choices", [])
        choices: dict[str, str] = {}
        for entry in choices_raw:
            if isinstance(entry, str) and len(entry) >= 3 and entry[1] == ":":
                choices[entry[0]] = entry[2:].strip()
            elif isinstance(entry, str):
                choices[entry[:1]] = entry
        samples.append(
            BenchmarkSample(
                id=item.get("id", f"seceval-{len(samples)}"),
                benchmark=BenchmarkType.SECEVAL,
                question=item["question"],
                choices=choices,
                answer=item.get("answer", ""),
                prompt=item["question"],
                metadata={
                    "source": item.get("source", ""),
                    "topics": item.get("topics", []),
                    "keyword": item.get("keyword", ""),
                    "source_file": path.name,
                },
            )
        )
    return samples


def _load_cti_bench(path: Path) -> list[BenchmarkSample]:
    samples: list[BenchmarkSample] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh, delimiter="\t")
        header = next(reader, None)
        if header is None:
            return samples
        for idx, row in enumerate(reader):
            if len(row) < 8:
                continue
            url, question, opt_a, opt_b, opt_c, opt_d, prompt_text, gt = (
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
            )
            samples.append(
                BenchmarkSample(
                    id=f"cti-{path.stem}-{idx}",
                    benchmark=BenchmarkType.CTI_BENCH,
                    question=question,
                    choices={"A": opt_a, "B": opt_b, "C": opt_c, "D": opt_d},
                    answer=gt.strip(),
                    prompt=prompt_text,
                    metadata={"url": url, "source_file": path.name},
                )
            )
    return samples


def _load_cyberpii(path: Path) -> list[BenchmarkSample]:
    samples: list[BenchmarkSample] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for idx, row in enumerate(reader):
            samples.append(
                BenchmarkSample(
                    id=f"cyberpii-{idx}",
                    benchmark=BenchmarkType.CYBERPII,
                    question=row.get("text", row.get("input", "")),
                    answer=row.get("gold", row.get("expected", "")),
                    prompt=row.get("text", row.get("input", "")),
                    metadata={
                        "source_file": path.name,
                        **{
                            k: (v if v is not None else "") for k, v in row.items() if k is not None
                        },
                    },
                )
            )
    return samples


_LOADERS: dict[BenchmarkType, Any] = {
    BenchmarkType.CYBERMETRIC: _load_cybermetric,
    BenchmarkType.SECEVAL: _load_seceval,
    BenchmarkType.CTI_BENCH: _load_cti_bench,
    BenchmarkType.CYBERPII: _load_cyberpii,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_dataset(
    benchmark: BenchmarkType | str,
    *,
    project_root: Path | None = None,
    file_override: Path | None = None,
) -> list[BenchmarkSample]:
    """Load and normalise benchmark samples.

    Parameters
    ----------
    benchmark:
        Which benchmark to load.
    project_root:
        Root of the DEF-CAI project (defaults to cwd).
    file_override:
        If given, load this single file instead of the registered paths.
    """
    benchmark = BenchmarkType(benchmark)
    loader = _LOADERS.get(benchmark)
    if loader is None:
        raise ValueError(f"No loader for benchmark {benchmark!r}")

    root = project_root or Path.cwd()

    if file_override is not None:
        resolved = file_override if file_override.is_absolute() else root / file_override
        return loader(resolved)

    paths = DATASET_PATHS.get(benchmark, [])
    samples: list[BenchmarkSample] = []
    for rel_path in paths:
        resolved = rel_path if rel_path.is_absolute() else root / rel_path
        if resolved.exists():
            samples.extend(loader(resolved))
    return samples


def list_datasets(project_root: Path | None = None) -> dict[str, dict[str, Any]]:
    """Return a registry summary: benchmark name -> file count, sample count, availability."""
    root = project_root or Path.cwd()
    info: dict[str, dict[str, Any]] = {}
    for bench, paths in DATASET_PATHS.items():
        resolved = [p if p.is_absolute() else root / p for p in paths]
        available = [p for p in resolved if p.exists()]
        info[bench.value] = {
            "files_registered": len(paths),
            "files_available": len(available),
            "available_paths": [str(p) for p in available],
        }
    return info
