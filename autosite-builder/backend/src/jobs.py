"""إدارة مهام البناء في الخلفية مع تتبّع الحالة والتقدّم."""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from .utils import setup_logger

# الحالات الممكنة للمهمة
PENDING = "pending"
RUNNING = "running"
DONE = "done"
FAILED = "failed"

MAX_LOGS = 500


def _now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class Job:
    """مهمة بناء واحدة."""

    id: str
    city: str
    category: str
    country: str = ""
    limit: int = 10
    status: str = PENDING
    built: int = 0
    found: int = 0
    selected: int = 0
    error: Optional[str] = None
    created_at: str = field(default_factory=_now)
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    logs: List[Dict[str, Any]] = field(default_factory=list)

    def add_log(self, event: str, data: Dict[str, Any]) -> None:
        """يضيف حدثاً مع الوقت، مع تحديد حجم السجل."""
        self.logs.append({"ts": _now(), "event": event, "data": data})
        if len(self.logs) > MAX_LOGS:
            del self.logs[: len(self.logs) - MAX_LOGS]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "city": self.city,
            "category": self.category,
            "country": self.country,
            "limit": self.limit,
            "status": self.status,
            "built": self.built,
            "found": self.found,
            "selected": self.selected,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "logs": self.logs,
        }


class JobManager:
    """يدير المهام في الخلفية؛ يسمح بمهمة نشطة واحدة فقط في الوقت نفسه."""

    def __init__(self, runner) -> None:
        # runner: دالة async (job) تُنفّذ البناء وتُبلّغ عبر job.add_log
        self._runner = runner
        self._jobs: Dict[str, Job] = {}
        self._active: Optional[str] = None
        self._lock = asyncio.Lock()

    def create(self, city: str, category: str, country: str = "", limit: int = 10) -> Job:
        """ينشئ مهمة جديدة ويعيدها."""
        job = Job(
            id=uuid.uuid4().hex[:12],
            city=city,
            category=category,
            country=country,
            limit=limit,
        )
        self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    def list(self) -> List[Job]:
        """يرجع المهام من الأحدث للأقدم."""
        return sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)

    @property
    def active_job_id(self) -> Optional[str]:
        return self._active

    def is_busy(self) -> bool:
        return self._active is not None

    async def start(self, job: Job) -> None:
        """يشغّل المهمة في الخلفية مع منع تشغيل مهمتين معاً."""
        async with self._lock:
            if self._active is not None:
                raise RuntimeError("توجد مهمة قيد التشغيل بالفعل")
            self._active = job.id
        asyncio.create_task(self._run(job))

    async def _run(self, job: Job) -> None:
        """ينفّذ المهمة ويحدّث حالتها، مع تنظيف المهام القديمة."""
        setup_logger("INFO")
        job.status = RUNNING
        job.started_at = _now()

        def progress(event: str, data: Dict[str, Any]) -> None:
            job.add_log(event, data)
            if event == "ranked":
                job.found = data.get("found", 0)
                job.selected = data.get("selected", 0)
            elif event == "built":
                job.built = data.get("built", job.built)

        try:
            await self._runner(job, progress)
            job.status = DONE
        except Exception as exc:  # noqa: BLE001
            job.status = FAILED
            job.error = str(exc)
            logger.error(f"فشلت المهمة {job.id}: {exc}")
        finally:
            job.finished_at = _now()
            self._active = None
            self._cleanup()

    def _cleanup(self, keep: int = 20) -> None:
        """يُبقي آخر عدد محدود من المهام المنتهية لمنع تضخّم الذاكرة."""
        finished = [
            j for j in self._jobs.values() if j.status in (DONE, FAILED)
        ]
        if len(finished) <= keep:
            return
        finished.sort(key=lambda j: j.finished_at or "")
        for old in finished[: len(finished) - keep]:
            self._jobs.pop(old.id, None)
