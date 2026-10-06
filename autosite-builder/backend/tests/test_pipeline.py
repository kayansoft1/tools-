"""اختبارات وحدة لخط الإنتاج، لا تحتاج مفاتيح API خارجية."""

import asyncio
import json
from pathlib import Path

import pytest

from src.builder import SiteBuilder
from src.content import ContentGenerator
from src.discovery import DISTRICTS_BY_CITY, Discovery
from src.models import Business, Enrichment
from src.qualification import CATEGORY_WEIGHTS, qualify, score_business
from src.utils import clean_json, slugify, translate_category


def make_business(**overrides) -> Business:
    data = dict(
        place_id="place-1",
        name="مطعم الأصالة",
        category="مطعم",
        city="جدة",
        country="السعودية",
        phone="+966500000000",
        rating=4.5,
        reviews_count=120,
    )
    data.update(overrides)
    return Business(**data)


def test_translate_category_known_and_unknown():
    assert translate_category("restaurant") == "مطعم"
    assert translate_category("cafe") == "مقهى"
    # غير معروف يرجع القيمة الافتراضية
    assert translate_category("zzz") == "أعمال"
    assert translate_category("") == "أعمال"


def test_slugify_handles_arabic_and_spaces():
    slug = slugify("مطعم الأصالة - جدة")
    assert " " not in slug
    assert slug
    assert slugify("Hello World") == "hello-world"


def test_clean_json_strips_code_fences():
    raw = "```json\n{\"a\": 1}\n```"
    assert json.loads(clean_json(raw)) == {"a": 1}
    assert json.loads(clean_json("{\"b\": 2}")) == {"b": 2}


def test_score_business_full_marks():
    b = make_business(category="عيادة", rating=5.0, reviews_count=200, phone="+1")
    # 30 (مراجعات) + 25 (تقييم) + 15 (هاتف) + 30 (فئة 1.0) = 100
    assert score_business(b) == pytest.approx(100.0)


def test_score_business_penalizes_missing_phone_and_unknown_category():
    b = make_business(category="غير معروف", rating=0.0, reviews_count=0, phone=None)
    # 0 + 0 + 0 + 0.5*30 = 15
    assert score_business(b) == pytest.approx(15.0)
    assert CATEGORY_WEIGHTS["مطعم"] == 0.6


def test_qualify_sorts_descending():
    low = make_business(place_id="low", category="مقهى", rating=2.0, reviews_count=1)
    high = make_business(place_id="high", category="عيادة", rating=5.0, reviews_count=300)
    result = qualify([low, high])
    assert [b.place_id for b in result] == ["high", "low"]


def test_districts_present_for_supported_cities():
    for city in ("جدة", "الرياض", "دبي"):
        assert len(DISTRICTS_BY_CITY[city]) > 5


def test_discovery_parses_place_without_website():
    discovery = Discovery(api_key="fake")
    place = {
        "id": "abc",
        "displayName": {"text": "متجر الورد"},
        "formattedAddress": "شارع 1، جدة",
        "primaryTypeDisplayName": {"text": "زهور"},
        "nationalPhoneNumber": "0500000000",
        "rating": 4.2,
        "userRatingCount": 33,
        "location": {"latitude": 21.5, "longitude": 39.2},
        "websiteUri": None,
    }
    business = discovery._parse_place(place, "جدة", "السعودية")
    assert business is not None
    assert business.place_id == "abc"
    assert business.name == "متجر الورد"
    assert business.has_website is False
    assert business.phone == "0500000000"
    assert business.rating == 4.2
    assert business.reviews_count == 33


def test_discovery_parses_place_with_website():
    discovery = Discovery(api_key="fake")
    place = {
        "id": "abc2",
        "displayName": {"text": "شركة"},
        "websiteUri": "https://example.com",
    }
    business = discovery._parse_place(place, "جدة", "السعودية")
    assert business.has_website is True
    assert business.website_url == "https://example.com"


def test_discovery_skips_place_without_id():
    discovery = Discovery(api_key="fake")
    assert discovery._parse_place({}, "جدة", "السعودية") is None


@pytest.mark.asyncio
async def test_discovery_deduplicates_across_districts(monkeypatch):
    discovery = Discovery(api_key="fake")
    shared = {
        "id": "dup-1",
        "displayName": {"text": "مكرر"},
        "types": ["restaurant"],
    }
    unique = {"id": "uniq-1", "displayName": {"text": "فريد"}, "types": ["cafe"]}

    async def fake_search_district(category, district, city):
        return [shared, unique]

    monkeypatch.setattr(discovery, "_search_district", fake_search_district)
    real_sleep = asyncio.sleep
    monkeypatch.setattr("src.discovery.asyncio.sleep", lambda *_: real_sleep(0))
    monkeypatch.setattr("src.discovery.DISTRICTS_BY_CITY", {"جدة": ["حي1", "حي2"]})

    results = await discovery.search("جدة", "مطاعم", "السعودية", limit=10)
    ids = [b.place_id for b in results]
    assert ids == ["dup-1", "uniq-1"]


def test_content_default_fallback_is_arabic():
    generator = ContentGenerator(api_key="")
    generator.client = None
    business = make_business()
    content = generator._default_content(business)
    assert business.name in content.short_description
    assert content.services
    assert content.faq
    assert content.seo_title == business.name


@pytest.mark.asyncio
async def test_content_generate_falls_back_without_client():
    generator = ContentGenerator(api_key="")
    generator.client = None
    business = make_business()
    content = await generator.generate(business, Enrichment(place_id=business.place_id))
    assert business.name in content.short_description


def test_builder_writes_valid_json(tmp_path: Path):
    builder = SiteBuilder(str(tmp_path))
    business = make_business()
    content = ContentGenerator(api_key="")._default_content(business)
    enrichment = Enrichment(place_id=business.place_id, instagram_url="https://instagram.com/x")
    place_id = builder.build(business, content, enrichment)

    output = tmp_path / "data" / f"{place_id}.json"
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["place_id"] == business.place_id
    assert data["name"] == business.name
    assert data["category"] == business.category
    assert data["city"] == business.city
    assert data["social"]["instagram_url"] == "https://instagram.com/x"
    assert data["content"]["seo_title"] == business.name
