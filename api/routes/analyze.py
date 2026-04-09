from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl

from pipeline.cloner import clone_repo
from pipeline.scanner import scan_repository
from pipeline.triage import triage_findings

router = APIRouter()


class AnalyzeRequest(BaseModel):
    repo_url: HttpUrl


@router.post("")
def analyze_repository(payload: AnalyzeRequest) -> dict[str, Any]:
    target_path = Path(clone_repo(str(payload.repo_url)))
    findings = scan_repository(target_path)
    triage = triage_findings(findings)
    return {"target": str(target_path), "findings": findings, "triage": triage}
