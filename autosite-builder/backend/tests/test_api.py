"""اختبارات نقاط النهاية في الـ API باستخدام TestClient (بدون شبكة خارجية)."""

from fastapi.testclient import TestClient

import api
from src.jobs import DONE, JobManager


def _client() -> TestClient:
    return TestClient(api.app)


def test_health_reports_key_presence():
    response = _client().get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert set(body["keys"]) == {"google_places", "gemini", "serpapi"}


def test_create_job_validates_input():
    response = _client().post("/api/jobs", json={"city": "", "category": "مطاعم"})
    assert response.status_code == 422


def test_get_missing_job_returns_404():
    assert _client().get("/api/jobs/nope").status_code == 404


def test_job_lifecycle_via_api(monkeypatch):
    captured = {}

    async def fake_process(city, category, country="", limit=10, progress=None):
        captured.update(city=city, category=category, country=country, limit=limit)
        if progress:
            progress("ranked", {"found": 4, "selected": 2})
            progress("built", {"name": "x", "built": 1})
        return 1

    monkeypatch.setattr(api, "process", fake_process)
    manager = JobManager(api._run_job)
    monkeypatch.setattr(api, "manager", manager)

    client = _client()
    created = client.post(
        "/api/jobs",
        json={"city": "جدة", "category": "مطاعم", "country": "السعودية", "limit": 2},
    )
    assert created.status_code == 201
    job_id = created.json()["id"]

    # المهمة قصيرة جداً؛ ننتظرها لتنتهي ثم نتحقق
    import time

    for _ in range(100):
        detail = client.get(f"/api/jobs/{job_id}").json()
        if detail["status"] == DONE:
            break
        time.sleep(0.02)

    assert detail["status"] == DONE
    assert detail["built"] == 1
    assert detail["found"] == 4
    assert captured == {"city": "جدة", "category": "مطاعم", "country": "السعودية", "limit": 2}
    assert any(log["event"] == "built" for log in detail["logs"])


def test_second_job_conflicts_while_busy(monkeypatch):
    manager = JobManager(api._run_job)
    # محاكاة مهمة قيد التشغيل (TestClient يعزل حلقة الأحداث لكل طلب)
    manager._active = "existing-job"
    monkeypatch.setattr(api, "manager", manager)

    client = _client()
    response = client.post("/api/jobs", json={"city": "الرياض", "category": "عيادات"})
    assert response.status_code == 409
