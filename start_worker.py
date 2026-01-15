"""Worker process for Railway deployment - runs the episode generator."""

import asyncio
import logging
import signal
import sys

# Ensure we're using the PostgreSQL database, not SQLite
if 'database_sqlite' in sys.modules:
    del sys.modules['database_sqlite']

from config import config
from database import db
from canon import canon
from episode_manager import episode_manager
from main import Orchestrator, signal_handler

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Entry point for worker process."""
    logger.info("AniGen Worker Starting on Railway...")
    logger.info(f"Mode: {config.generation_mode}")
    logger.info(f"Database: {config.database_url}")
    logger.info(f"Scenes per episode: {config.scenes_per_episode}")
    logger.info(f"Scene interval: {config.scene_generation_interval_minutes} minutes")

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    orchestrator = Orchestrator()
    await orchestrator.run()


if __name__ == "__main__":
    print("=" * 60)
    print("  AniGen Worker - Railway Deployment")
    print("=" * 60)
    print()
    print("Press Ctrl+C to stop")
    print()

    asyncio.run(main())
