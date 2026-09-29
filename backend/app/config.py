from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    triage_provider: str = "simulated"
    openrouter_api_key: str = ""
    openrouter_model: str = ""
    database_url: str = "postgresql+asyncpg://civicpulse:change-me@localhost:5432/civicpulse"
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_per_minute: int = 10
    stats_cache_ttl_seconds: int = 30
    triage_cache_ttl_seconds: int = 86400
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
