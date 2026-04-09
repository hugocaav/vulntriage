from fastapi import FastAPI

from api.routes.analyze import router as analyze_router
from api.routes.reports import router as reports_router

app = FastAPI(title="vulntriage API", version="0.1.0")
app.include_router(analyze_router, prefix="/analyze", tags=["analyze"])
app.include_router(reports_router, prefix="/reports", tags=["reports"])


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

