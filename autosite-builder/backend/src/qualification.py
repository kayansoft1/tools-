"""ترتيب المنشآت حسب الأولوية التجارية."""

from typing import Dict, List

from .models import Business

# أوزان الفئات بحسب قيمتها التجارية
CATEGORY_WEIGHTS: Dict[str, float] = {
    "عيادة": 1.0,
    "محامي": 1.0,
    "مقاولات": 0.9,
    "عقارات": 0.8,
    "صالون": 0.7,
    "مطعم": 0.6,
    "مقهى": 0.5,
}


def score_business(business: Business) -> float:
    """يحسب نتيجة أولوية منشأة من 0 إلى 100."""
    reviews_score = min(business.reviews_count / 100, 1) * 30
    rating_score = (business.rating / 5) * 25
    phone_score = 15 if business.phone else 0
    weight = CATEGORY_WEIGHTS.get(business.category, 0.5)
    weight_score = weight * 30
    return reviews_score + rating_score + phone_score + weight_score


def qualify(businesses: List[Business]) -> List[Business]:
    """يرتب المنشآت تنازلياً حسب النتيجة."""
    return sorted(businesses, key=score_business, reverse=True)
