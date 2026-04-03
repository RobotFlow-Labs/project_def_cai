"""Safety policy profiles for different operational contexts.

Paper reference: Section 2, Section 4 — semi-autonomous operation with
human oversight.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SafetyPolicy(BaseModel):
    """Defines the safety envelope for a CAI session."""

    name: str
    allowed_tools: list[str] = Field(default_factory=list)
    blocked_commands: list[str] = Field(default_factory=list)
    require_hitl: bool = True
    max_turns: int = 100
    allow_network: bool = False
    allow_destructive: bool = False
    target_scope: str = "lab-only"
    metadata: dict[str, Any] = Field(default_factory=dict)


AUDIT_POLICY = SafetyPolicy(
    name="audit",
    allowed_tools=["linux_command", "python_exec", "code_review"],
    require_hitl=False,
    allow_network=False,
    allow_destructive=False,
    target_scope="lab-only",
    metadata={"description": "Read-only audit mode for safe inspection"},
)

RESTRICTED_POLICY = SafetyPolicy(
    name="restricted",
    allowed_tools=["linux_command", "python_exec", "code_review", "network_scan"],
    blocked_commands=["rm -rf", "mkfs", "dd of=/dev"],
    require_hitl=True,
    allow_network=True,
    allow_destructive=False,
    target_scope="lab-only",
    metadata={"description": "Standard restricted mode with HITL for network actions"},
)

LAB_POLICY = SafetyPolicy(
    name="lab",
    allowed_tools=[
        "linux_command",
        "python_exec",
        "code_review",
        "network_scan",
        "exploit_runner",
        "ssh_command",
    ],
    require_hitl=True,
    allow_network=True,
    allow_destructive=True,
    target_scope="lab-only",
    metadata={"description": "Full lab mode — destructive actions allowed with HITL"},
)

POLICY_REGISTRY: dict[str, SafetyPolicy] = {
    "audit": AUDIT_POLICY,
    "restricted": RESTRICTED_POLICY,
    "lab": LAB_POLICY,
}


def get_policy(name: str) -> SafetyPolicy:
    policy = POLICY_REGISTRY.get(name)
    if policy is None:
        raise ValueError(f"Unknown policy: {name!r}. Available: {list(POLICY_REGISTRY)}")
    return policy
