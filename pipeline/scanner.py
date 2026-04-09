from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_command(command: list[str], cwd: Path | None = None) -> dict[str, Any]:
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def scan_repository(repo_path: str | Path) -> dict[str, Any]:
    path = Path(repo_path).resolve()
    return {
        "target": str(path),
        "semgrep": run_command(
            ["semgrep", "scan", "--config", "auto", "--json", str(path)]
        ),
        "bandit": run_command(["bandit", "-r", "-f", "json", str(path)]),
    }


def write_report(report: dict[str, Any], output_path: str | Path) -> Path:
    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return destination


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python -m pipeline.scanner <repo_path> <output_json>")

    report = scan_repository(sys.argv[1])
    output = write_report(report, sys.argv[2])
    print(output)


if __name__ == "__main__":
    main()

