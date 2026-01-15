"""Configuration management for AniGen system."""

import os
from decimal import Decimal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Config(BaseSettings):
    """System configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env" if os.path.exists(".env") else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix=""
    )

    # Database - will read from DATABASE_URL env var
    database_url: str = Field(
        default="postgresql://anigen_user:anigen_password@localhost:5432/anigen"
    )

    # API Keys
    anthropic_api_key: str = Field(default="")
    google_ai_api_key: str = Field(default="")
    openai_api_key: str = Field(default="")
    kling_access_key: str = Field(default="")
    kling_secret_key: str = Field(default="")

    # AWS S3
    aws_access_key_id: str = Field(default="")
    aws_secret_access_key: str = Field(default="")
    aws_s3_bucket: str = Field(default="anigen-videos")
    aws_region: str = Field(default="us-east-1")

    # System Configuration
    generation_mode: str = Field(default="mock")  # mock or real
    scene_duration_seconds: int = Field(default=30)
    scenes_per_episode: int = Field(default=6)
    scene_generation_interval_minutes: int = Field(default=10)

    # Cost Limits
    max_daily_cost_usd: Decimal = Field(default=Decimal("1000.00"))
    max_monthly_cost_usd: Decimal = Field(default=Decimal("25000.00"))

    # Director Model
    director_model: str = Field(default="claude-opus-4-5-20251101")
    director_max_tokens: int = Field(default=200000)

    # Logging
    log_level: str = Field(default="INFO")


# Global config instance
config = Config()

# Debug: Log what DATABASE_URL we're actually using
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Config loaded - DATABASE_URL from env: {os.getenv('DATABASE_URL', 'NOT SET')}")
logger.info(f"Config loaded - database_url value: {config.database_url}")
