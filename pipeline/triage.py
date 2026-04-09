from __future__ import annotations

import json
import os
from typing import Any

try:
    from anthropic import Anthropic
except ImportError:  # pragma: no cover
    Anthropic = None


SYSTEM_PROMPT = """You are a security triage assistant.
Prioritize exploitability, business impact, and evidence quality.
Return strict JSON with severity, confidence, rationale, and remediation."""


def build_triage_prompt(findings: dict[str, Any]) -> str:
    return (
        "Review the static analysis findings below and identify likely false positives, "
        "high-signal vulnerabilities, and recommended prioritization.\n\n"
        f"{json.dumps(findings, indent=2)}"
    )


def triage_findings(findings: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or Anthropic is None:
        return {
            "status": "stubbed",
            "summary": "LLM triage not executed. Set ANTHROPIC_API_KEY and install anthropic.",
            "prioritized_findings": findings,
        }

    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_triage_prompt(findings)}],
    )
    text_blocks = [block.text for block in message.content if hasattr(block, "text")]
    return {
        "status": "completed",
        "model": "claude-3-5-sonnet-latest",
        "response": "\n".join(text_blocks),
    }

