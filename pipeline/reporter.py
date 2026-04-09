from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json_report(payload: dict[str, Any], output_path: str | Path) -> Path:
    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return destination


def write_markdown_report(payload: dict[str, Any], output_path: str | Path) -> Path:
    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Vulnerability Triage Report",
        "",
        f"- Status: {payload.get('status', 'unknown')}",
        f"- Model: {payload.get('model', 'n/a')}",
        "",
        "## Summary",
        "",
        str(payload.get("summary") or payload.get("response") or "No summary available."),
    ]
    destination.write_text("\n".join(lines), encoding="utf-8")
    return destination

