from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from pipeline.cloner import clone_repo
    from pipeline.reporter import write_json_report
    from pipeline.scanner import scan_repo
except ModuleNotFoundError:  # pragma: no cover
    from cloner import clone_repo
    from reporter import write_json_report
    from scanner import scan_repo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"


def _report_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _relative_to_project(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT).as_posix())
    except ValueError:
        return str(path.resolve())


def _build_report_path(cloned_repo_path: Path) -> Path:
    report_name = f"{cloned_repo_path.name}-{_report_timestamp()}.json"
    return REPORTS_DIR / report_name


def _print_summary(cloned_repo_path: Path, report: dict[str, object], report_path: Path) -> None:
    summary = report["summary"]
    if not isinstance(summary, dict):
        raise RuntimeError("Scan report summary is malformed.")

    by_severity = summary.get("by_severity", {})
    if not isinstance(by_severity, dict):
        raise RuntimeError("Scan report severity summary is malformed.")

    print(f"✓ Cloned: {cloned_repo_path.name}")
    print(
        "✓ Scanned: "
        f"{summary.get('total_findings', 0)} findings "
        f"(HIGH: {by_severity.get('HIGH', 0)}, "
        f"MEDIUM: {by_severity.get('MEDIUM', 0)}, "
        f"LOW: {by_severity.get('LOW', 0)})"
    )
    print(f"✓ Report saved: {_relative_to_project(report_path)}")


def run_pipeline(repo_url: str) -> Path:
    try:
        cloned_repo_path = Path(clone_repo(repo_url))
    except Exception as exc:
        raise SystemExit(f"Clone failed: {exc}") from exc

    try:
        report = scan_repo(str(cloned_repo_path))
    except Exception as exc:
        raise SystemExit(f"Scan failed: {exc}") from exc

    report_path = _build_report_path(cloned_repo_path)
    write_json_report(report, report_path)
    _print_summary(cloned_repo_path, report, report_path)
    return report_path


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Clone a public GitHub repository and run the VulnTriage scanner."
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="GitHub repository URL, for example https://github.com/we45/Vulnerable-Flask-App",
    )
    args = parser.parse_args()

    run_pipeline(args.repo)


if __name__ == "__main__":
    main()
