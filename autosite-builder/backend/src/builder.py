"""بناء ملف بيانات JSON لكل منشأة داخل مجلد frontend/data."""

import json
import os
from typing import Any, Dict

from loguru import logger

from .models import Business, Enrichment, SiteContent


class SiteBuilder:
    """يكتب ملف JSON جاهزاً ليقرأه الـ frontend ويبنيه Vercel."""

    def __init__(self, frontend_path: str) -> None:
        self.frontend_path = frontend_path
        self.data_dir = os.path.join(frontend_path, "data")

    def build(
        self, business: Business, content: SiteContent, enrichment: Enrichment
    ) -> str:
        """ينشئ ملف place_id.json ويرجع place_id."""
        payload: Dict[str, Any] = {
            "place_id": business.place_id,
            "name": business.name,
            "category": business.category,
            "city": business.city,
            "phone": business.phone,
            "whatsapp": business.phone,
            "address": business.address,
            "latitude": business.latitude,
            "longitude": business.longitude,
            "rating": business.rating,
            "reviews_count": business.reviews_count,
            "content": content.model_dump(),
            "social": enrichment.model_dump(),
        }
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            file_path = os.path.join(self.data_dir, f"{business.place_id}.json")
            with open(file_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
        except Exception as exc:  # noqa: BLE001
            logger.error(f"فشل بناء ملف الموقع {business.place_id}: {exc}")
        return business.place_id
