"""يشغّل خط الإنتاج ثم ينشر ملفات JSON المولَّدة إلى GitHub لتُبنى على Vercel.

الاستخدام:
    python publish.py "جدة" "مطاعم" 5
    python publish.py "الرياض" "عيادات" 10 --country "السعودية"
    python publish.py "جدة" "مطاعم" 5 --no-push   # بناء الملفات دون دفع
"""

import argparse
import asyncio
import os
import subprocess
import sys

from loguru import logger

from main import FRONTEND_PATH, process
from src.utils import setup_logger

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _run_git(*args: str) -> int:
    """ينفذ أمر git داخل جذر المستودع ويرجع رمز الخروج."""
    result = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)
    if result.stdout.strip():
        logger.info(result.stdout.strip())
    if result.stderr.strip():
        logger.warning(result.stderr.strip())
    return result.returncode


def publish(message: str) -> None:
    """يضيف ملفات data المولَّدة ويدفعها إلى الفرع الحالي."""
    data_path = os.path.relpath(os.path.join(FRONTEND_PATH, "data"), REPO_ROOT)
    _run_git("add", data_path)
    if _run_git("diff", "--cached", "--quiet") == 0:
        logger.info("لا توجد ملفات جديدة للنشر.")
        return
    _run_git("commit", "-m", message)
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if _run_git("push", "origin", branch) != 0:
        logger.error("فشل الدفع إلى GitHub. تحقق من صلاحيات المستودع.")
        sys.exit(1)
    logger.success(f"تم نشر المواقع الجديدة على الفرع {branch}.")


async def main() -> None:
    parser = argparse.ArgumentParser(description="AutoSite Builder - تشغيل ونشر")
    parser.add_argument("city", nargs="?", default="جدة")
    parser.add_argument("category", nargs="?", default="مطاعم")
    parser.add_argument("limit", nargs="?", type=int, default=5)
    parser.add_argument("--country", default="")
    parser.add_argument("--no-push", action="store_true", help="بناء الملفات دون دفع")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    setup_logger(args.log_level)
    built = await process(args.city, args.category, args.country, args.limit)
    if built == 0:
        logger.warning("لم يُبنَ أي موقع؛ لا يوجد ما يُنشر.")
        return
    if args.no_push:
        logger.info(f"تم بناء {built} موقع دون دفع (--no-push).")
        return
    publish(f"Build {built} sites for {args.category} in {args.city}")


if __name__ == "__main__":
    asyncio.run(main())
