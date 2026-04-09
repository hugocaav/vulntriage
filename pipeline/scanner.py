from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SEVERITY_LEVELS = ("HIGH", "MEDIUM", "LOW")


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _has_python_files(repo_path: Path) -> bool:
    return any(repo_path.rglob("*.py"))


def _run_bandit(repo_path: Path) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, "-m", "bandit", "-r", str(repo_path), "-f", "json"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode not in {0, 1}:
        stderr = result.stderr.strip() or "Bandit execution failed."
        raise RuntimeError(stderr)

    stdout = result.stdout.strip()
    if not stdout:
        return {"results": []}

    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Bandit returned invalid JSON output.") from exc


def _run_semgrep_placeholder() -> dict[str, Any]:
    return {"findings": [], "note": "semgrep runs in Docker"}


def _extract_code_snippet(repo_path: Path, file_path: Path, line_number: int, fallback: str) -> str:
    absolute_path = repo_path / file_path
    try:
        lines = absolute_path.read_text(encoding="utf-8").splitlines()
    except (FileNotFoundError, OSError, UnicodeDecodeError):
        lines = []

    if 1 <= line_number <= len(lines):
        return lines[line_number - 1].rstrip()

    for line in fallback.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.split(maxsplit=1)[0].rstrip(":").isdigit():
            parts = stripped.split(maxsplit=1)
            return parts[1].rstrip() if len(parts) > 1 else ""
        return stripped

    return ""


def _normalize_bandit_results(repo_path: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []

    for index, result in enumerate(payload.get("results", []), start=1):
        severity = str(result.get("issue_severity", "LOW")).upper()
        if severity not in SEVERITY_LEVELS:
            severity = "LOW"

        absolute_file = Path(result.get("filename", ""))
        try:
            relative_file = absolute_file.resolve().relative_to(repo_path.resolve())
        except ValueError:
            relative_file = Path(result.get("filename", "")).relative_to(
                Path(result.get("filename", "")).anchor
            ) if absolute_file.is_absolute() else Path(result.get("filename", ""))

        line_number = int(result.get("line_number") or 0)
        cwe_info = result.get("issue_cwe")
        cwe_id = None
        if isinstance(cwe_info, dict) and cwe_info.get("id") is not None:
            cwe_id = f"CWE-{cwe_info['id']}"

        normalized.append(
            {
                "id": f"finding_{index:03d}",
                "tool": "bandit",
                "rule_id": result.get("test_id"),
                "severity": severity,
                "file": relative_file.as_posix(),
                "line": line_number,
                "code_snippet": _extract_code_snippet(
                    repo_path=repo_path,
                    file_path=relative_file,
                    line_number=line_number,
                    fallback=str(result.get("code", "")),
                ),
                "message": result.get("issue_text", ""),
                "cwe": cwe_id,
            }
        )

    return normalized


def _build_report(repo_path: Path, findings: list[dict[str, Any]]) -> dict[str, Any]:
    by_severity = {level: 0 for level in SEVERITY_LEVELS}
    for finding in findings:
        by_severity[finding["severity"]] += 1

    return {
        "repo_path": str(repo_path.resolve()),
        "scanned_at": _utc_timestamp(),
        "summary": {
            "total_findings": len(findings),
            "by_severity": by_severity,
            "tools_run": ["bandit"],
        },
        "findings": findings,
    }


def scan_repo(repo_path: str) -> dict[str, Any]:
    path = Path(repo_path).resolve()
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"Repository path does not exist: {path}")

    _run_semgrep_placeholder()

    if not _has_python_files(path):
        return _build_report(path, [])

    bandit_payload = _run_bandit(path)
    findings = _normalize_bandit_results(path, bandit_payload)
    return _build_report(path, findings)


def scan_repository(repo_path: str | Path) -> dict[str, Any]:
    """Backward-compatible wrapper around scan_repo."""
    return scan_repo(str(repo_path))


def write_report(report: dict[str, Any], output_path: str | Path) -> Path:
    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Bandit against a cloned repository.")
    parser.add_argument(
        "--repo",
        required=True,
        help="Path to the cloned repository, for example outputs/repos/we45__Vulnerable-Flask-App",
    )
    parser.add_argument(
        "--output",
        help="Optional JSON file path where the normalized report will be written.",
    )
    args = parser.parse_args()

    report = scan_repo(args.repo)
    if args.output:
        print(write_report(report, args.output))
        return

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
