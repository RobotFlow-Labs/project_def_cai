"""Compute backend helpers for Mac-first development and CUDA deployment."""

from __future__ import annotations

from enum import StrEnum
from importlib.util import find_spec


class ComputeBackend(StrEnum):
    AUTO = "auto"
    MLX = "mlx"
    CUDA = "cuda"
    CPU = "cpu"


def _has_module(name: str) -> bool:
    return find_spec(name) is not None


def resolve_backend(preferred: str = ComputeBackend.AUTO.value) -> ComputeBackend:
    """Resolve the active compute backend without hard-importing optional stacks."""
    try:
        requested = ComputeBackend(preferred)
    except ValueError as exc:
        raise ValueError(f"Unsupported backend: {preferred}") from exc

    if requested is ComputeBackend.MLX:
        return ComputeBackend.MLX if _has_module("mlx") else ComputeBackend.CPU
    if requested is ComputeBackend.CUDA:
        if _has_module("torch"):
            import torch

            return ComputeBackend.CUDA if torch.cuda.is_available() else ComputeBackend.CPU
        return ComputeBackend.CPU
    if requested is ComputeBackend.CPU:
        return ComputeBackend.CPU

    if _has_module("mlx"):
        return ComputeBackend.MLX
    if _has_module("torch"):
        import torch

        if torch.cuda.is_available():
            return ComputeBackend.CUDA
    return ComputeBackend.CPU


def dependency_hint(backend: str) -> str:
    resolved = resolve_backend(backend)
    if resolved is ComputeBackend.MLX:
        return "Install the optional `mac` extra for Apple Silicon MLX support."
    if resolved is ComputeBackend.CUDA:
        return "Install the optional `cuda` extra on the Linux GPU server."
    return "The base install is sufficient for CPU-only validation."
