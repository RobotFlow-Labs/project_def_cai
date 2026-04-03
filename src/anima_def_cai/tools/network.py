"""Network and remote-access tool stubs with credential gating."""

from __future__ import annotations

from .common import ToolObservation


def ssh_probe(host: str, user: str, port: int = 22) -> ToolObservation:
    if not host or not user:
        return ToolObservation(
            tool_name="ssh_probe",
            command=f"{user}@{host}:{port}",
            stderr="host and user are required",
            exit_code=1,
            allowed=False,
        )
    return ToolObservation(
        tool_name="ssh_probe",
        command=f"{user}@{host}:{port}",
        stdout="SSH probe gated; live connections are not enabled in this build",
        metadata={"stub": True},
    )


def capture_traffic(interface: str, duration_seconds: int = 5) -> ToolObservation:
    return ToolObservation(
        tool_name="capture_traffic",
        command=f"{interface}:{duration_seconds}",
        stdout="Traffic capture adapter scaffolded; packet capture is disabled in local tests",
        metadata={"stub": True},
    )
