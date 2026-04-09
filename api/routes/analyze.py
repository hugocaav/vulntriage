from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl

from pipeline.cloner import clone_repository
from pipeline.scanner import scan_repository
from pipeline.triage import triage_findings

router = APIRouter()


class AnalyzeRequest(BaseModel):
    repo_url: HttpUrl


@router.post("")
def analyze_repository(payload: AnalyzeRequest) -> dict[str, Any]:
    workspace = Path("workspace")
    target_path = clone_repository(str(payload.repo_url), workspace / "target")
    findings = scan_repository(target_path)
    triage = triage_findings(findings)
    return {"target": str(target_path), "findings": findings, "triage": triage}

