"""Configuration management for AniGen system."""

import os
from decimal import Decimal
from pydantic_settings import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    """System configuration loaded from environment variables."""

    # Database
    database_url: str = Field(default="postgresql://anigen_user:anigen_password@localhost:5432/anigen")

    # API Keys
    anthropic_api_key: str = Field(default="")
    google_ai_api_key: str = Field(default="")
    openai_api_key: str = Field(default="")

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

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global config instance
config = Config()
