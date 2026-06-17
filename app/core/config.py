"""Typed configuration for SourceLens AI."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SOURCELENS_",
        extra="ignore",
    )

    app_name: str = "SourceLens AI"
    log_level: str = "INFO"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    ollama_timeout_seconds: int = Field(default=60, ge=1, le=300)
    search_max_results: int = Field(default=5, ge=1, le=10)
    search_timeout_seconds: int = Field(default=20, ge=1, le=60)
    search_user_agent: str = (
        "SourceLensAI/1.0 "
        "(https://github.com/local/sourcelens-ai; contact: sourcelens-local@example.com)"
    )
    report_output_dir: Path = Path("data/reports")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
