"""البحث عن روابط حسابات التواصل الاجتماعي عبر SerpAPI."""

import asyncio
from typing import Optional

from loguru import logger
from serpapi import GoogleSearch

from .models import Business
from .models import Enrichment as EnrichmentData

PLATFORM_DOMAINS = {
    "instagram": "instagram.com",
    "tiktok": "tiktok.com",
    "snapchat": "snapchat.com",
    "facebook": "facebook.com",
}


class Enrichment:
    """يجمع روابط إنستقرام وتيك توك وسناب شات وفيسبوك."""

    def __init__(self, serpapi_key: str) -> None:
        self.serpapi_key = serpapi_key

    async def enrich(self, business: Business) -> EnrichmentData:
        """يرجع كائن EnrichmentData فيه الروابط المتاحة."""
        return EnrichmentData(
            place_id=business.place_id,
            instagram_url=await self._find_social(business.name, business.city, "instagram"),
            tiktok_url=await self._find_social(business.name, business.city, "tiktok"),
            snapchat_url=await self._find_social(business.name, business.city, "snapchat"),
            facebook_url=await self._find_social(business.name, business.city, "facebook"),
        )

    async def _find_social(self, name: str, city: str, platform: str) -> Optional[str]:
        """يبحث عن أول رابط يحتوي على اسم المنصة دون حجب حلقة الأحداث."""
        domain = PLATFORM_DOMAINS.get(platform)
        if not domain:
            return None
        try:
            return await asyncio.to_thread(self._search_link, name, city, platform, domain)
        except Exception as exc:  # noqa: BLE001
            logger.error(f"فشل البحث عن {platform} لـ {name}: {exc}")
        return None

    def _search_link(self, name: str, city: str, platform: str, domain: str) -> Optional[str]:
        """تنفيذ استدعاء SerpAPI المتزامن في خيط منفصل."""
        params = {
            "engine": "google",
            "q": f"{name} {city} {platform}",
            "api_key": self.serpapi_key,
        }
        results = GoogleSearch(params).get_dict()
        for item in results.get("organic_results", []) or []:
            link = item.get("link", "")
            if domain in link:
                return link
        return None
