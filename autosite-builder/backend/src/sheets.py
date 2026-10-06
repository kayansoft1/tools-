"""إضافة صف متابعة لكل منشأة في Google Sheets."""

from datetime import UTC, datetime

import gspread
from loguru import logger

from .models import Business

HEADERS = ["Name", "Phone", "City", "Category", "Site URL", "Status", "Notes", "Date"]


class Sheets:
    """يتعامل مع شيت CRM للمتابعة."""

    def __init__(self, creds_file: str, sheet_name: str) -> None:
        self.creds_file = creds_file
        self.sheet_name = sheet_name
        self.worksheet = None
        try:
            client = gspread.service_account(filename=self.creds_file)
            self.worksheet = client.open(self.sheet_name).sheet1
        except Exception as exc:  # noqa: BLE001
            logger.error(f"فشل الاتصال بـ Google Sheets: {exc}")

    def _ensure_headers(self) -> None:
        """يضيف صف العناوين فقط إذا كان الشيت فارغاً، حتى لا نزيح بيانات موجودة."""
        try:
            if not self.worksheet:
                return
            existing = self.worksheet.row_values(1)
            if not existing:
                self.worksheet.insert_row(HEADERS, index=1)
            elif existing != HEADERS:
                logger.warning("عنوان الشيت مختلف عن المتوقع؛ لم يتم تعديله.")
        except Exception as exc:  # noqa: BLE001
            logger.error(f"فشل ضبط عناوين الشيت: {exc}")

    def add_lead(self, business: Business, site_url: str) -> None:
        """يضيف صفاً جديداً لعميل محتمل."""
        try:
            if not self.worksheet:
                return
            self._ensure_headers()
            row = [
                business.name,
                business.phone or "",
                business.city,
                business.category,
                site_url,
                "new",
                "",
                datetime.now(UTC).strftime("%Y-%m-%d"),
            ]
            self.worksheet.append_row(row)
        except Exception as exc:  # noqa: BLE001
            logger.error(f"فشل إضافة lead لـ {business.name}: {exc}")
