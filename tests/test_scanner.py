from pipeline.scanner import write_report


def test_write_report_creates_json_file(tmp_path):
    destination = tmp_path / "findings.json"
    result = write_report({"status": "ok"}, destination)

    assert result == destination
    assert destination.exists()
    assert '"status": "ok"' in destination.read_text(encoding="utf-8")

