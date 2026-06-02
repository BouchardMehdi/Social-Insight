from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Social Insight Platform"
    api_prefix: str = "/api"
    environment: str = "local"
    storage_backend: Literal["memory"] = "memory"

    google_cloud_project: str | None = None
    bigquery_dataset: str = "social_insight"
    bigquery_posts_table: str = "posts"
    bigquery_location: str = "EU"

    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8080",
        ]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SOCIAL_INSIGHT_",
        env_nested_delimiter="__",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
