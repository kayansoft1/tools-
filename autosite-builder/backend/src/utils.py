"""دوال مساعدة مشتركة بين كل الوحدات."""

import re
import sys
from typing import Dict

from loguru import logger

# خريطة تحويل الفئات من الإنجليزي إلى العربي
CATEGORY_MAP: Dict[str, str] = {
    "dentist": "عيادة",
    "clinic": "عيادة",
    "doctor": "طبيب",
    "lawyer": "محامي",
    "attorney": "محامي",
    "contractor": "مقاولات",
    "real_estate": "عقارات",
    "salon": "صالون",
    "beauty_salon": "صالون",
    "restaurant": "مطعم",
    "cafe": "مقهى",
    "bakery": "مخبز",
    "gym": "صالة رياضية",
    "car_repair": "ورشة سيارات",
    "car_dealer": "معرض سيارات",
}


def slugify(text: str) -> str:
    """يحول نصاً إنجليزياً إلى slug صالح للاستخدام في الروابط."""
    value = (text or "").strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_-]+", "-", value)
    return value.strip("-")


def clean_json(text: str) -> str:
    """يزيل علامات ```json و ``` من ردود الذكاء الاصطناعي قبل التحويل إلى JSON."""
    if not text:
        return ""
    cleaned = text.replace("```json", "").replace("```JSON", "").replace("```", "")
    return cleaned.strip()


def setup_logger(log_level: str = "INFO") -> None:
    """يضبط loguru حسب مستوى التسجيل المطلوب."""
    logger.remove()
    logger.add(sys.stderr, level=(log_level or "INFO").upper())


def translate_category(category: str) -> str:
    """يرجع الفئة بالعربي، أو 'أعمال' كقيمة افتراضية."""
    if not category:
        return "أعمال"
    key = category.strip().lower().replace(" ", "_")
    return CATEGORY_MAP.get(key, "أعمال")
