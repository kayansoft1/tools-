"""اختبار بنية المشروع بقيم وهمية دون الحاجة لمفاتيح API."""

import os

from src.builder import SiteBuilder
from src.models import Business, Enrichment, SiteContent

FRONTEND_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)


def main() -> None:
    """يشغّل builder فقط لكتابة ملف JSON تجريبي."""
    business = Business(
        place_id="test-place",
        name="مطعم الاختبار",
        category="مطعم",
        city="جدة",
        country="SA",
        address="شارع الاختبار، جدة",
        phone="+966500000000",
        rating=4.6,
        reviews_count=120,
        latitude=21.4858,
        longitude=39.1925,
        has_website=False,
        website_url=None,
    )
    enrichment = Enrichment(
        place_id="test-place",
        instagram_url="https://instagram.com/test",
        tiktok_url=None,
        snapchat_url=None,
        facebook_url="https://facebook.com/test",
    )
    content = SiteContent(
        short_description="مطعم الاختبار يقدم أشهى الأطباق في جدة.",
        long_description="مطعم الاختبار في جدة، نقدم أفضل الخدمات لعملائنا الكرام.",
        services=[
            {"name": "خدمة عملاء متميزة", "description": "فريق جاهز لخدمتك.", "icon": "🤝"},
            {"name": "جودة عالية", "description": "نلتزم بأعلى المعايير.", "icon": "⭐"},
            {"name": "أسعار منافسة", "description": "أفضل قيمة.", "icon": "💰"},
        ],
        faq=[
            {"q": "ما هي أوقات العمل؟", "a": "نعمل طوال الأسبوع."},
            {"q": "كيف يمكنني التواصل؟", "a": "عبر الهاتف أو واتساب."},
        ],
        seo_title="مطعم الاختبار - جدة",
        seo_description="مطعم الاختبار يقدم أشهى الأطباق في جدة.",
    )

    builder = SiteBuilder(FRONTEND_PATH)
    place_id = builder.build(business, content, enrichment)
    print(f"تم إنشاء ملف الاختبار بنجاح: {place_id}.json")


if __name__ == "__main__":
    main()
