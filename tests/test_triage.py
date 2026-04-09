from pipeline.triage import build_triage_prompt, triage_findings


def test_build_triage_prompt_embeds_findings():
    prompt = build_triage_prompt({"finding": "test"})
    assert "finding" in prompt
    assert "test" in prompt


def test_triage_returns_stub_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = triage_findings({"finding": "test"})

    assert result["status"] == "stubbed"

