"""نماذج البيانات (Pydantic) المستخدمة في كل مراحل المشروع."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Business(BaseModel):
    """منشأة واحدة مستخرجة من Google Places."""

    place_id: str
    name: str
    category: str = "أعمال"
    city: str = ""
    country: str = ""
    address: str = ""
    phone: Optional[str] = None
    rating: float = 0.0
    reviews_count: int = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    has_website: bool = False
    website_url: Optional[str] = None


class Enrichment(BaseModel):
    """روابط حسابات التواصل الاجتماعي لمنشأة واحدة."""

    place_id: str
    instagram_url: Optional[str] = None
    tiktok_url: Optional[str] = None
    snapchat_url: Optional[str] = None
    facebook_url: Optional[str] = None


class SiteContent(BaseModel):
    """المحتوى العربي المولَّد للموقع."""

    short_description: str = ""
    long_description: str = ""
    services: List[Dict[str, Any]] = Field(default_factory=list)
    faq: List[Dict[str, Any]] = Field(default_factory=list)
    seo_title: str = ""
    seo_description: str = ""
