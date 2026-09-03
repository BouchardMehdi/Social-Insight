from functools import lru_cache
from typing import Literal, Self

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Social Insight Platform"
    api_prefix: str = "/api"
    environment: str = "local"
    storage_backend: Literal["bigquery", "memory"] = "bigquery"
    seed_on_startup: bool = False
    seed_posts_count: int = Field(default=600, ge=0, le=5000)
    analysis_workers: int = Field(default=2, ge=1, le=8)
    analysis_recovery_limit: int = Field(default=1000, ge=0, le=10000)
    log_level: str = "INFO"

    google_cloud_project: str | None = None
    bigquery_dataset: str = "social_insight"
    bigquery_posts_table: str = "posts"
    bigquery_users_table: str = "users"
    bigquery_workspaces_table: str = "workspaces"
    bigquery_memberships_table: str = "workspace_memberships"
    bigquery_location: str = "EU"
    google_application_credentials: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "GOOGLE_APPLICATION_CREDENTIALS",
            "SOCIAL_INSIGHT_GOOGLE_APPLICATION_CREDENTIALS",
        ),
    )

    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8080",
        ]
    )

    auth_secret_key: str = Field(default="local-development-secret-change-me", min_length=32)
    auth_token_expire_minutes: int = Field(default=720, ge=5, le=10080)
    auth_token_issuer: str = "social-insight"
    demo_email: str = "demo@social-insight.local"
    demo_password: str = "demo-social-insight"
    demo_display_name: str = "Compte démo"
    demo_workspace_name: str = "Espace de démonstration"

    @model_validator(mode="after")
    def reject_default_production_secret(self) -> Self:
        if (
            self.environment.casefold() == "production"
            and self.auth_secret_key == "local-development-secret-change-me"
        ):
            raise ValueError("SOCIAL_INSIGHT_AUTH_SECRET_KEY must be changed in production.")
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SOCIAL_INSIGHT_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
