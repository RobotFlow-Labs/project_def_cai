"""Input/output guardrails for safe CAI operation.

Blocks prompt-injection patterns, dangerous commands, and policy-violating
tool invocations before they reach the execution layer.

Paper reference: Section 2, Section 4 —
"Human-In-The-Loop (HITL) module is therefore not merely a feature but a
critical cornerstone..."
"""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class GuardrailDecision(StrEnum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    ESCALATE = "escalate"


class GuardrailResult(BaseModel):
    decision: GuardrailDecision
    rule: str
    reason: str
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Blocked patterns
# ---------------------------------------------------------------------------

PROMPT_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+a?\s*(new|different)", re.IGNORECASE),
    re.compile(r"system\s*:\s*you\s+are", re.IGNORECASE),
    re.compile(r"forget\s+(everything|all|your\s+instructions)", re.IGNORECASE),
    re.compile(r"disregard\s+(all|any|your)", re.IGNORECASE),
    re.compile(r"\bDAN\b.*\bjailbreak\b", re.IGNORECASE),
]

DANGEROUS_COMMAND_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\brm\s+-rf\s+/"),
    re.compile(r"\bmkfs\b"),
    re.compile(r"\bdd\s+.*of=/dev/\b"),
    re.compile(r":\(\)\s*\{\s*:\|:&\s*\}\s*;:"),  # fork bomb
    re.compile(r"\bshutdown\b.*\bnow\b", re.IGNORECASE),
    re.compile(r"\breboot\b", re.IGNORECASE),
    re.compile(r"\biptables\s+-F\b"),
    re.compile(r"\bchmod\s+777\s+/\b"),
    re.compile(r"\bcurl\b.*\|\s*(ba)?sh\b"),
    re.compile(r"\bwget\b.*\|\s*(ba)?sh\b"),
]

WARN_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bnmap\b", re.IGNORECASE),
    re.compile(r"\bmetasploit\b", re.IGNORECASE),
    re.compile(r"\bexploit\b", re.IGNORECASE),
    re.compile(r"\bpasswd\b", re.IGNORECASE),
    re.compile(r"\bsudo\b", re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# Checkers
# ---------------------------------------------------------------------------


def check_input(text: str) -> GuardrailResult:
    """Check user/agent input for prompt injection or dangerous content."""
    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern.search(text):
            return GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                rule="prompt_injection",
                reason=f"Prompt injection pattern detected: {pattern.pattern}",
            )
    return GuardrailResult(decision=GuardrailDecision.ALLOW, rule="input_clean", reason="OK")


def check_command(command: str) -> GuardrailResult:
    """Check a shell command for dangerous patterns."""
    for pattern in DANGEROUS_COMMAND_PATTERNS:
        if pattern.search(command):
            return GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                rule="dangerous_command",
                reason=f"Dangerous command pattern: {pattern.pattern}",
            )
    for pattern in WARN_PATTERNS:
        if pattern.search(command):
            return GuardrailResult(
                decision=GuardrailDecision.WARN,
                rule="warn_command",
                reason=f"Sensitive command pattern: {pattern.pattern}",
            )
    return GuardrailResult(decision=GuardrailDecision.ALLOW, rule="command_clean", reason="OK")


def check_output(text: str) -> GuardrailResult:
    """Check output for sensitive data leakage patterns."""
    sensitive_patterns = [
        (re.compile(r"(?:password|passwd|secret)\s*[:=]\s*\S+", re.IGNORECASE), "credential_leak"),
        (re.compile(r"[A-Za-z0-9+/]{40,}={0,2}"), "possible_base64_secret"),
        (re.compile(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"), "private_key_leak"),
    ]
    for pattern, rule_name in sensitive_patterns:
        if pattern.search(text):
            return GuardrailResult(
                decision=GuardrailDecision.WARN,
                rule=rule_name,
                reason=f"Sensitive data pattern in output: {rule_name}",
            )
    return GuardrailResult(decision=GuardrailDecision.ALLOW, rule="output_clean", reason="OK")
