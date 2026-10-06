"""توليد محتوى الموقع باللغة العربية عبر Gemini Flash (حزمة google-genai)."""

import asyncio
import json
from typing import Any, Dict

from google import genai
from loguru import logger

from .models import Business, Enrichment, SiteContent
from .utils import clean_json

MODEL_NAME = "gemini-2.0-flash"


class ContentGenerator:
    """يولّد وصفاً وخدمات وأسئلة شائعة وبيانات SEO لمنشأة."""

    def __init__(self, api_key: str, model_name: str = MODEL_NAME) -> None:
        self.api_key = api_key
        self.model_name = model_name
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as exc:  # noqa: BLE001
            logger.error(f"فشل تهيئة Gemini: {exc}")
            self.client = None

    async def generate(self, business: Business, enrichment: Enrichment) -> SiteContent:
        """يرسل البرومبت إلى Gemini ويعيد SiteContent."""
        prompt = self._build_prompt(business, enrichment)
        try:
            if not self.client:
                raise RuntimeError("عميل Gemini غير مهيأ")
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
            )
            raw_text = getattr(response, "text", "") or ""
            data: Dict[str, Any] = json.loads(clean_json(raw_text))
            return SiteContent(
                short_description=data.get("short_description", ""),
                long_description=data.get("long_description", ""),
                services=data.get("services", []) or [],
                faq=data.get("faq", []) or [],
                seo_title=data.get("seo_title", business.name),
                seo_description=data.get("seo_description", ""),
            )
        except Exception as exc:  # noqa: BLE001
            logger.error(f"فشل توليد المحتوى لـ {business.name}: {exc}")
            return self._default_content(business)

    def _build_prompt(self, business: Business, enrichment: Enrichment) -> str:
        """يبني برومبت عربي يطلب JSON فقط."""
        social_lines = []
        if enrichment.instagram_url:
            social_lines.append(f"إنستقرام: {enrichment.instagram_url}")
        if enrichment.tiktok_url:
            social_lines.append(f"تيك توك: {enrichment.tiktok_url}")
        if enrichment.snapchat_url:
            social_lines.append(f"سناب شات: {enrichment.snapchat_url}")
        if enrichment.facebook_url:
            social_lines.append(f"فيسبوك: {enrichment.facebook_url}")
        social_text = "\n".join(social_lines) if social_lines else "لا توجد حسابات معروفة"

        return f"""
أنت كاتب محتوى تسويقي محترف باللغة العربية.
اكتب محتوى موقع إلكتروني للمنشأة التالية:

الاسم: {business.name}
الفئة: {business.category}
المدينة: {business.city}
العنوان: {business.address}
الهاتف: {business.phone or "غير متوفر"}
التقييم: {business.rating}
عدد المراجعات: {business.reviews_count}
حسابات التواصل:
{social_text}

أعد النتيجة بصيغة JSON فقط دون أي نص إضافي، بالبنية التالية:
{{
  "short_description": "وصف قصير في حدود 50 كلمة",
  "long_description": "وصف طويل في حدود 200 كلمة",
  "services": [
    {{"name": "اسم الخدمة", "description": "وصف الخدمة", "icon": "إيموجي"}},
    ... ست خدمات
  ],
  "faq": [
    {{"q": "السؤال", "a": "الجواب"}},
    ... خمسة أسئلة
  ],
  "seo_title": "عنوان SEO جذاب",
  "seo_description": "وصف SEO في حدود 160 حرفاً"
}}
""".strip()

    def _default_content(self, business: Business) -> SiteContent:
        """محتوى افتراضي عند فشل Gemini أو فشل تحويل JSON."""
        short = f"مرحباً بكم في {business.name}"
        return SiteContent(
            short_description=short,
            long_description=(
                f"{business.name} في {business.city}، نقدم أفضل الخدمات لعملائنا الكرام."
            ),
            services=[
                {"name": "خدمة عملاء متميزة", "description": "فريق جاهز لخدمتك.", "icon": "🤝"},
                {"name": "جودة عالية", "description": "نلتزم بأعلى معايير الجودة.", "icon": "⭐"},
                {"name": "أسعار منافسة", "description": "أفضل قيمة مقابل سعرك.", "icon": "💰"},
            ],
            faq=[
                {"q": "ما هي أوقات العمل؟", "a": "نعمل خلال أيام الأسبوع وفق أوقات معلنة."},
                {"q": "كيف يمكنني التواصل معكم؟", "a": "يمكنك التواصل عبر الهاتف أو واتساب."},
            ],
            seo_title=business.name,
            seo_description=short,
        )
