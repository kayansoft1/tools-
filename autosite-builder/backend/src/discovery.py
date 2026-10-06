"""البحث عن المنشآت عبر Google Places API الإصدار v1 (غير متزامن)."""

import asyncio
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed

from .models import Business
from .utils import translate_category

# أحياء المدن المدعومة بشكل ثابت
JEDDAH_DISTRICTS = [
    "الروضة", "الحمراء", "السلامة", "الشاطئ", "النعيم", "الصفا", "المروة",
    "البوادي", "الزهراء", "الفيصلية", "الشرفية", "البغدادية", "الصحيفة",
    "الجامعة", "الثغر", "الرحاب", "السامر", "النسيم", "أبحر",
]

RIYADH_DISTRICTS = [
    "العليا", "الملز", "النخيل", "الياسمين", "الملقا", "حطين", "الصحافة",
    "الوادي", "الربوة", "الروضة", "السليمانية", "المعذر", "العقيق",
    "غرناطة", "النرجس", "القيروان", "قرطبة", "المونسية",
]

DUBAI_DISTRICTS = [
    "ديرة", "بر دبي", "جميرا", "المرقبات", "الدفاع", "البرشاء", "القصيص",
    "النهدة", "الرقة", "مردف",
]

DISTRICTS_BY_CITY: Dict[str, List[str]] = {
    "جدة": JEDDAH_DISTRICTS,
    "الرياض": RIYADH_DISTRICTS,
    "دبي": DUBAI_DISTRICTS,
}

SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

FIELD_MASK = (
    "places.id,places.displayName,places.formattedAddress,places.rating,"
    "places.userRatingCount,places.nationalPhoneNumber,places.websiteUri,"
    "places.types,places.location"
)


class Discovery:
    """يبحث عن المنشآت في مدينة وفئة محددتين."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def search(
        self, city: str, category: str, country: str = "", limit: int = 10
    ) -> List[Business]:
        """يبحث في كل أحياء المدينة ويرجع قائمة من Business."""
        results: List[Business] = []
        seen: set[str] = set()
        districts = self._get_districts(city)
        for district in districts:
            if len(results) >= limit:
                break
            places = await self._search_district(category, district, city)
            for place in places:
                try:
                    business = self._parse_place(place, city, country)
                    # الأحياء قد تتداخل في النتائج؛ نتجاهل أي منشأة مكررة
                    if business is None or business.place_id in seen:
                        continue
                    seen.add(business.place_id)
                    results.append(business)
                except Exception as exc:  # noqa: BLE001
                    logger.error(f"فشل تحويل منشأة: {exc}")
            await asyncio.sleep(2)
        return results

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    async def _request_page(
        self, client: httpx.AsyncClient, query: str, page_token: str | None = None
    ) -> Dict[str, Any]:
        """يرسل طلباً واحداً مع إعادة المحاولة عند الفشل."""
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": FIELD_MASK,
        }
        body: Dict[str, Any] = {
            "textQuery": query,
            "languageCode": "ar",
        }
        if page_token:
            body["pageToken"] = page_token
        response = await client.post(SEARCH_URL, headers=headers, json=body, timeout=30.0)
        response.raise_for_status()
        return response.json()

    async def _search_district(
        self, category: str, district: str, city: str
    ) -> List[Dict[str, Any]]:
        """يبحث في حي واحد مع دعم حتى 3 صفحات من النتائج."""
        query = f"{category} في {district} {city}"
        places: List[Dict[str, Any]] = []
        try:
            async with httpx.AsyncClient() as client:
                page_token: str | None = None
                for _ in range(3):
                    data = await self._request_page(client, query, page_token)
                    places.extend(data.get("places", []) or [])
                    page_token = data.get("nextPageToken")
                    if not page_token:
                        break
                    await asyncio.sleep(2)
        except Exception as exc:  # noqa: BLE001
            logger.error(f"فشل البحث في الحي {district}: {exc}")
        return places

    def _get_districts(self, city: str) -> List[str]:
        """يرجع قائمة أحياء المدينة أو القيمة الافتراضية."""
        return DISTRICTS_BY_CITY.get((city or "").strip(), ["وسط المدينة"])

    def _parse_place(
        self, place: Dict[str, Any], city: str, country: str
    ) -> Optional[Business]:
        """يحول عنصر Places API إلى كائن Business، أو None إذا كان بلا معرّف."""
        place_id = place.get("id")
        if not place_id:
            logger.warning("تم تجاهل منشأة بلا place_id.")
            return None
        display_name = place.get("displayName") or {}
        location = place.get("location") or {}
        types = place.get("types") or []
        raw_category = types[0] if types else ""
        website = place.get("websiteUri")
        if isinstance(display_name, dict):
            name = display_name.get("text", "")
        else:
            name = str(display_name)
        return Business(
            place_id=place_id,
            name=name,
            category=translate_category(raw_category),
            city=city,
            country=country,
            address=place.get("formattedAddress", "") or "",
            phone=place.get("nationalPhoneNumber"),
            rating=float(place.get("rating") or 0.0),
            reviews_count=int(place.get("userRatingCount") or 0),
            latitude=location.get("latitude"),
            longitude=location.get("longitude"),
            has_website=bool(website),
            website_url=website,
        )
