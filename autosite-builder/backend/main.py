"""نقطة التشغيل الرئيسية: تشغّل خط الإنتاج كاملاً من البحث حتى المتابعة."""

import asyncio
import os
import sys

from loguru import logger

from src.builder import SiteBuilder
from src.config import settings
from src.content import ContentGenerator
from src.db import Database
from src.discovery import Discovery
from src.enrichment import Enrichment
from src.qualification import qualify
from src.sheets import Sheets
from src.utils import setup_logger

# مسار الـ frontend نسبةً لمجلد backend
FRONTEND_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)


async def process(city: str, category: str, country: str = "", limit: int = 10) -> int:
    """ينفذ كل مراحل خط الإنتاج ويرجع عدد المواقع المبنية."""
    database = Database(settings.database_url)
    database.create_tables()

    discovery = Discovery(settings.google_places_api_key)
    businesses = await discovery.search(city, category, country, limit * 3)

    # استبعاد كل منشأة عندها موقع إلكتروني
    without_website = [b for b in businesses if not b.has_website]

    ranked = qualify(without_website)[:limit]

    enrichment_service = Enrichment(settings.serpapi_key)
    content_generator = ContentGenerator(settings.gemini_api_key, settings.gemini_model)
    builder = SiteBuilder(FRONTEND_PATH)
    sheets = Sheets(settings.google_sheets_creds, settings.google_sheets_name)

    built_count = 0
    for business in ranked:
        try:
            database.insert_business(business)
            enrichment = await enrichment_service.enrich(business)
            content = await content_generator.generate(business, enrichment)
            place_id = builder.build(business, content, enrichment)
            site_url = f"/s/{place_id}"
            database.insert_site(place_id, site_url, content.model_dump())
            sheets.add_lead(business, site_url)
            built_count += 1
            logger.info(f"تم بناء موقع: {business.name} ({place_id})")
        except Exception as exc:  # noqa: BLE001
            logger.error(f"فشل معالجة منشأة {getattr(business, 'name', '?')}: {exc}")

    database.close()
    logger.success(f"اكتمل البناء: {built_count} موقع.")
    return built_count


if __name__ == "__main__":
    setup_logger(settings.log_level)
    city_arg = sys.argv[1] if len(sys.argv) > 1 else "جدة"
    category_arg = sys.argv[2] if len(sys.argv) > 2 else "مطاعم"
    limit_arg = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    country_arg = sys.argv[4] if len(sys.argv) > 4 else ""
    asyncio.run(process(city_arg, category_arg, country_arg, limit_arg))
