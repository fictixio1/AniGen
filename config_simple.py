"""Simple configuration without Pydantic."""

import os


class Config:
    """Simple configuration class."""

    def __init__(self):
        # System Configuration
        self.generation_mode = "mock"
        self.scene_duration_seconds = 30
        self.scenes_per_episode = 6
        self.scene_generation_interval_minutes = 10

        # Logging
        self.log_level = "INFO"


# Global config instance
config = Config()
