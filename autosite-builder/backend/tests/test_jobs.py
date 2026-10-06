"""اختبارات مدير المهام والـ API، لا تحتاج مفاتيح أو قاعدة بيانات."""

import asyncio

import pytest

from src.jobs import DONE, FAILED, Job, JobManager


async def _wait(job: Job, timeout: float = 2.0) -> None:
    """ينتظر انتهاء المهمة (نجاحاً أو فشلاً) أو انتهاء المهلة."""
    elapsed = 0.0
    while job.status not in (DONE, FAILED) and elapsed < timeout:
        await asyncio.sleep(0.02)
        elapsed += 0.02


@pytest.mark.asyncio
async def test_job_runs_and_reports_progress():
    async def runner(job, progress):
        progress("ranked", {"found": 5, "selected": 3})
        for i in range(3):
            progress("built", {"name": f"b{i}", "built": i + 1})

    manager = JobManager(runner)
    job = manager.create("جدة", "مطاعم", "السعودية", 3)
    await manager.start(job)
    await _wait(job)

    assert job.status == DONE
    assert job.found == 5
    assert job.selected == 3
    assert job.built == 3
    assert job.finished_at is not None
    assert not manager.is_busy()


@pytest.mark.asyncio
async def test_job_failure_is_recorded():
    async def runner(job, progress):
        raise RuntimeError("boom")

    manager = JobManager(runner)
    job = manager.create("جدة", "مطاعم")
    await manager.start(job)
    await _wait(job)

    assert job.status == FAILED
    assert job.error == "boom"
    assert not manager.is_busy()


@pytest.mark.asyncio
async def test_only_one_job_runs_at_a_time():
    release = asyncio.Event()

    async def runner(job, progress):
        await release.wait()

    manager = JobManager(runner)
    first = manager.create("جدة", "مطاعم")
    await manager.start(first)
    assert manager.is_busy()

    second = manager.create("الرياض", "عيادات")
    with pytest.raises(RuntimeError):
        await manager.start(second)

    release.set()
    await _wait(first)
    assert not manager.is_busy()


@pytest.mark.asyncio
async def test_job_logs_are_capped():
    async def runner(job, progress):
        for i in range(700):
            progress("built", {"i": i})

    manager = JobManager(runner)
    job = manager.create("جدة", "مطاعم")
    await manager.start(job)
    await _wait(job)

    assert len(job.logs) <= 500


def test_cleanup_keeps_only_recent_jobs():
    manager = JobManager(lambda job, progress: None)
    for i in range(30):
        job = manager.create("جدة", "مطاعم")
        job.status = DONE
        job.finished_at = f"2026-01-01T00:00:{i:02d}"
    manager._cleanup(keep=20)
    assert len(manager.list()) == 20
