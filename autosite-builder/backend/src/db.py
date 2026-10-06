"""التعامل مع قاعدة بيانات PostgreSQL عبر psycopg2."""

from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import Json, RealDictCursor
from loguru import logger

from .models import Business


class Database:
    """يدير الاتصال والجداول والعمليات الأساسية."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.conn = None
        try:
            self.conn = psycopg2.connect(self.database_url)
        except Exception as exc:  # noqa: BLE001
            logger.error(f"فشل الاتصال بقاعدة البيانات: {exc}")

    def create_tables(self) -> None:
        """ينشئ الجدولين businesses و sites إذا لم يوجدا."""
        statements = [
            """
            CREATE TABLE IF NOT EXISTS businesses (
                id SERIAL PRIMARY KEY,
                place_id TEXT UNIQUE NOT NULL,
                name TEXT,
                category TEXT,
                city TEXT,
                country TEXT,
                address TEXT,
                phone TEXT,
                rating DOUBLE PRECISION,
                reviews_count INTEGER,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                has_website BOOLEAN DEFAULT FALSE,
                website_url TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS sites (
                id SERIAL PRIMARY KEY,
                place_id TEXT,
                site_url TEXT,
                content JSONB,
                deployed_at TIMESTAMP DEFAULT NOW()
            );
            """,
        ]
        try:
            if not self.conn:
                return
            with self.conn.cursor() as cur:
                for statement in statements:
                    cur.execute(statement)
            self.conn.commit()
        except Exception as exc:  # noqa: BLE001
            logger.error(f"فشل إنشاء الجداول: {exc}")
            if self.conn:
                self.conn.rollback()

    def insert_business(self, business: Business) -> None:
        """يضيف منشأة مع تجاهل التكرار."""
        try:
            if not self.conn:
                return
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO businesses (
                        place_id, name, category, city, country, address, phone,
                        rating, reviews_count, latitude, longitude, has_website, website_url
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (place_id) DO NOTHING;
                    """,
                    (
                        business.place_id,
                        business.name,
                        business.category,
                        business.city,
                        business.country,
                        business.address,
                        business.phone,
                        business.rating,
                        business.reviews_count,
                        business.latitude,
                        business.longitude,
                        business.has_website,
                        business.website_url,
                    ),
                )
            self.conn.commit()
        except Exception as exc:  # noqa: BLE001
            logger.error(f"فشل إضافة منشأة {business.place_id}: {exc}")
            if self.conn:
                self.conn.rollback()

    def get_businesses(self) -> List[Dict[str, Any]]:
        """يرجع كل المنشآت المخزنة."""
        try:
            if not self.conn:
                return []
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM businesses ORDER BY created_at DESC;")
                return [dict(row) for row in cur.fetchall()]
        except Exception as exc:  # noqa: BLE001
            logger.error(f"فشل قراءة المنشآت: {exc}")
            return []

    def insert_site(
        self, place_id: str, site_url: str, content: Optional[Dict[str, Any]] = None
    ) -> None:
        """يحفظ الموقع المولَّد في جدول sites."""
        try:
            if not self.conn:
                return
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO sites (place_id, site_url, content)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING;
                    """,
                    (place_id, site_url, Json(content or {})),
                )
            self.conn.commit()
        except Exception as exc:  # noqa: BLE001
            logger.error(f"فشل حفظ الموقع {place_id}: {exc}")
            if self.conn:
                self.conn.rollback()

    def close(self) -> None:
        """يغلق الاتصال بقاعدة البيانات."""
        try:
            if self.conn:
                self.conn.close()
        except Exception as exc:  # noqa: BLE001
            logger.error(f"فشل إغلاق الاتصال: {exc}")
