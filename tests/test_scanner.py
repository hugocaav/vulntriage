from __future__ import annotations

import json
import subprocess
from pathlib import Path

from pipeline.scanner import scan_repo, write_report


def test_scan_repo_returns_empty_findings_for_repo_without_python(tmp_path):
    (tmp_path / "README.md").write_text("no python here", encoding="utf-8")

    report = scan_repo(str(tmp_path))

    assert report["repo_path"] == str(tmp_path.resolve())
    assert report["summary"]["total_findings"] == 0
    assert report["summary"]["tools_run"] == ["bandit"]
    assert report["findings"] == []


def test_scan_repo_normalizes_bandit_output(monkeypatch, tmp_path):
    source_file = tmp_path / "app.py"
    source_file.write_text("password = 'secret'\nprint(password)\n", encoding="utf-8")

    bandit_output = {
        "results": [
            {
                "filename": str(source_file),
                "test_id": "B105",
                "issue_severity": "LOW",
                "line_number": 1,
                "issue_text": "Possible hardcoded password.",
                "issue_cwe": {"id": 259},
                "code": "1 password = 'secret'",
            }
        ]
    }

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=1,
            stdout=json.dumps(bandit_output),
            stderr="",
        )

    monkeypatch.setattr("pipeline.scanner.subprocess.run", fake_run)

    report = scan_repo(str(tmp_path))

    assert report["summary"]["total_findings"] == 1
    assert report["summary"]["by_severity"] == {"HIGH": 0, "MEDIUM": 0, "LOW": 1}
    assert report["findings"] == [
        {
            "id": "finding_001",
            "tool": "bandit",
            "rule_id": "B105",
            "severity": "LOW",
            "file": "app.py",
            "line": 1,
            "code_snippet": "password = 'secret'",
            "message": "Possible hardcoded password.",
            "cwe": "CWE-259",
        }
    ]


def test_write_report_creates_json_file(tmp_path):
    destination = tmp_path / "findings.json"
    result = write_report({"status": "ok"}, destination)

    assert result == destination
    assert destination.exists()
    assert '"status": "ok"' in destination.read_text(encoding="utf-8")
