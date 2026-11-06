from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    app_env: str = "development"
    database_url: str = "postgresql+psycopg://agro:agro_local_dev@localhost:5432/agroseason"
    redis_url: str = "redis://127.0.0.1:6379/0"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    media_dir: Path = Path("./data/media")

    openai_api_key: str = Field(default="", repr=False)
    openai_model: str = "gpt-4o-mini"
    serper_api_key: str = Field(default="", repr=False)

    rate_limit_per_minute: int = 120
    research_rate_limit_per_hour: int = 5
    serper_daily_limit: int = 100
    openai_daily_limit: int = 100
    monthly_budget_usd: float = 10.0
    research_cache_ttl_days: int = 30
    research_job_max_attempts: int = 3
    http_timeout_seconds: float = 15.0
    max_download_bytes: int = 5 * 1024 * 1024
    max_page_chars: int = 60000
    trust_proxy_headers: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
