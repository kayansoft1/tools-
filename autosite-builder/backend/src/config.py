"""إعدادات المشروع المقروءة من متغيرات البيئة."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """يقرأ كل المتغيرات المطلوبة من ملف .env."""

    google_places_api_key: str = ""
    gemini_api_key: str = ""
    serpapi_key: str = ""
    database_url: str = "postgresql://user:pass@host:5432/db"
    google_sheets_creds: str = "creds.json"
    google_sheets_name: str = "AutoSite CRM"
    log_level: str = "INFO"
    gemini_model: str = "gemini-2.0-flash"
    # أصول مسموح لها بالاتصال بالـ API (مفصولة بفواصل)، الافتراضي الكل للتطوير
    api_cors_origins: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
