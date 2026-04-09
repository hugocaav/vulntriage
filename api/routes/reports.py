from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("")
def list_reports() -> dict[str, list[str]]:
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    files = sorted(path.name for path in reports_dir.iterdir() if path.is_file())
    return {"reports": files}


@router.get("/{report_name}")
def get_report(report_name: str) -> dict[str, str]:
    report_path = Path("reports") / report_name
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    return {"name": report_name, "content": report_path.read_text(encoding="utf-8")}

