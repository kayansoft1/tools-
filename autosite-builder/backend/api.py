"""واجهة برمجية (REST API) للتحكم بالمشروع من لوحة الويب.

التشغيل:
    uvicorn api:app --host 0.0.0.0 --port 8000
أو:
    python api.py
"""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel, Field

from main import process
from src.config import settings
from src.db import Database
from src.jobs import Job, JobManager
from src.utils import setup_logger

app = FastAPI(title="AutoSite Builder API", version="0.3.0")

# الواجهة الأمامية (Next.js) تعمل على منفذ مختلف في التطوير
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.api_cors_origins.split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)


class BuildRequest(BaseModel):
    """جسم طلب بدء مهمة بناء."""

    city: str = Field(default="جدة", min_length=1)
    category: str = Field(default="مطاعم", min_length=1)
    country: str = ""
    limit: int = Field(default=5, ge=1, le=50)


class JobInfo(BaseModel):
    """معلومات مختصرة عن مهمة."""

    id: str
    city: str
    category: str
    country: str
    limit: int
    status: str
    built: int
    found: int
    selected: int
    error: str | None = None
    created_at: str
    started_at: str | None = None
    finished_at: str | None = None


async def _run_job(job: Job, progress) -> None:
    """ينفّذ خط الإنتاج الحقيقي مع تمرير دالة التقدّم."""
    await process(
        job.city,
        job.category,
        job.country,
        job.limit,
        progress=progress,
    )


manager = JobManager(_run_job)


def _summary(job: Job) -> JobInfo:
    return JobInfo(**{k: v for k, v in job.to_dict().items() if k != "logs"})


@app.get("/api/health")
def health() -> dict:
    """فحص جاهزية الخدمة والمفاتيح."""
    return {
        "status": "ok",
        "busy": manager.is_busy(),
        "active_job": manager.active_job_id,
        "keys": {
            "google_places": bool(settings.google_places_api_key),
            "gemini": bool(settings.gemini_api_key),
            "serpapi": bool(settings.serpapi_key),
        },
    }


@app.get("/api/config")
def get_config() -> dict:
    """القيم الافتراضية للواجهة (دون كشف أي مفاتيح)."""
    return {
        "gemini_model": settings.gemini_model,
        "sheets_name": settings.google_sheets_name,
    }


@app.get("/api/jobs", response_model=list[JobInfo])
def list_jobs() -> list[JobInfo]:
    """كل المهام من الأحدث للأقدم."""
    return [_summary(job) for job in manager.list()]


@app.post("/api/jobs", response_model=JobInfo, status_code=201)
async def create_job(payload: BuildRequest) -> JobInfo:
    """ينشئ مهمة بناء جديدة ويشغّلها في الخلفية."""
    if manager.is_busy():
        raise HTTPException(status_code=409, detail="توجد مهمة قيد التشغيل بالفعل")
    job = manager.create(payload.city, payload.category, payload.country, payload.limit)
    try:
        await manager.start(job)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    logger.info(f"بدأت مهمة {job.id}: {payload.category} في {payload.city}")
    return _summary(job)


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    """حالة مهمة واحدة مع كل سجلّات التقدّم."""
    job = manager.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="المهمة غير موجودة")
    return job.to_dict()


@app.get("/api/leads")
def list_leads(limit: int = 100) -> dict:
    """المنشآت المخزّنة في قاعدة البيانات."""
    database = Database(settings.database_url)
    try:
        rows = database.get_businesses()
    finally:
        database.close()
    return {"count": len(rows), "items": rows[:limit]}


if __name__ == "__main__":
    import uvicorn

    setup_logger(settings.log_level)
    port = int(os.environ.get("API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
