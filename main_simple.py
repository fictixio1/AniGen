"""Simple version using SQLite - no PostgreSQL needed!"""

# Monkey patch to use SQLite instead of PostgreSQL
import sys
import database_sqlite
sys.modules['database'] = database_sqlite

# Now import everything else
import asyncio
import logging
import signal
from datetime import datetime
from decimal import Decimal
from typing import Dict

from config import config
from database_sqlite import db
from canon import canon
from episode_manager import episode_manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

shutdown_flag = False


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    global shutdown_flag
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_flag = True


class MockDirector:
    """Mock Director for testing."""

    async def plan_episode(self, episode_number: int, context: Dict) -> Dict:
        """Generate a mock episode plan with 6 scenes."""
        logger.info(f"Director planning episode {episode_number}")

        scenes = []
        for i in range(1, config.scenes_per_episode + 1):
            scenes.append({
                "scene_in_episode": i,
                "video_prompt": f"Episode {episode_number}, Scene {i}: Mock anime scene with characters in action",
                "narrative_summary": f"In scene {i}, the characters continue their journey"
            })

        return {
            "episode_number": episode_number,
            "episode_summary": f"Episode {episode_number}: A thrilling continuation of the story",
            "scenes": scenes,
            "estimated_cost": Decimal("27.66")
        }


class MockVideoGenerator:
    """Mock video generator."""

    async def generate_video(self, prompt: str, duration: int) -> Dict:
        """Simulate video generation."""
        logger.info(f"Generating {duration}s video: {prompt[:50]}...")
        await asyncio.sleep(0.1)

        return {
            "video_url": f"mock://video/{datetime.now().timestamp()}.mp4",
            "duration": duration,
            "cost": Decimal("4.50")
        }


class Orchestrator:
    """Main orchestration loop."""

    def __init__(self):
        self.director = MockDirector()
        self.video_generator = MockVideoGenerator()

    async def generate_episode(self):
        """Generate one complete episode (6 scenes)."""
        try:
            state = await canon.get_series_state()
            episode_number = state["current_episode"]

            logger.info(f"\n{'='*60}")
            logger.info(f"Starting Episode {episode_number}")
            logger.info(f"{'='*60}")

            await canon.update_series_state(system_status="planning_episode")

            context = await canon.build_director_context()
            episode_plan = await self.director.plan_episode(episode_number, context)

            await episode_manager.log_generation_event(
                scene_number=None,
                level="INFO",
                component="director",
                message=f"Planned episode {episode_number}: {episode_plan['episode_summary']}"
            )

            episode_id = await episode_manager.start_episode(
                episode_number=episode_number,
                director_plan=str(episode_plan),
                episode_summary=episode_plan["episode_summary"]
            )

            global_scene_number = state["total_scenes"] + 1

            for scene_plan in episode_plan["scenes"]:
                if shutdown_flag:
                    logger.info("Shutdown requested, stopping episode generation")
                    return

                scene_in_episode = scene_plan["scene_in_episode"]
                logger.info(f"\nGenerating Scene {scene_in_episode}/6 (Global #{global_scene_number})")

                scene_id = await episode_manager.create_scene(
                    episode_id=episode_id,
                    scene_number=global_scene_number,
                    scene_in_episode=scene_in_episode,
                    video_prompt=scene_plan["video_prompt"],
                    narrative_summary=scene_plan["narrative_summary"],
                    duration_seconds=config.scene_duration_seconds
                )

                video_result = await self.video_generator.generate_video(
                    prompt=scene_plan["video_prompt"],
                    duration=config.scene_duration_seconds
                )

                await episode_manager.complete_scene(
                    scene_id=scene_id,
                    video_url=video_result["video_url"],
                    cost_usd=video_result["cost"],
                    retry_count=0
                )

                logger.info(f"✓ Scene {scene_in_episode} completed: {video_result['video_url']}")

                global_scene_number += 1

                if scene_in_episode < config.scenes_per_episode and not shutdown_flag:
                    wait_seconds = config.scene_generation_interval_minutes * 60
                    logger.info(f"Waiting {config.scene_generation_interval_minutes} minutes until next scene...")

                    for _ in range(wait_seconds):
                        if shutdown_flag:
                            break
                        await asyncio.sleep(1)

            if not shutdown_flag:
                await episode_manager.complete_episode(episode_id)

                episode = await episode_manager.get_episode(episode_number)
                logger.info(f"\n{'='*60}")
                logger.info(f"Episode {episode_number} Complete!")
                logger.info(f"Total Cost: ${episode['total_cost_usd']}")
                logger.info(f"Duration: {episode['total_duration_seconds']}s")
                logger.info(f"{'='*60}\n")

                await canon.update_series_state(
                    current_episode=episode_number + 1,
                    current_scene_in_episode=1,
                    system_status="idle"
                )

        except Exception as e:
            logger.error(f"Error generating episode: {e}", exc_info=True)
            await canon.update_series_state(system_status="error")
            await episode_manager.log_generation_event(
                scene_number=None,
                level="ERROR",
                component="orchestrator",
                message=f"Episode generation failed: {str(e)}",
                error_details=str(e)
            )

    async def run(self):
        """Main loop - continuously generate episodes."""
        logger.info("AniGen Orchestrator Starting...")
        logger.info(f"Mode: {config.generation_mode}")
        logger.info(f"Database: SQLite (anigen.db)")
        logger.info(f"Scenes per episode: {config.scenes_per_episode}")
        logger.info(f"Scene interval: {config.scene_generation_interval_minutes} minutes")

        await db.connect()

        try:
            while not shutdown_flag:
                await self.generate_episode()

                if not shutdown_flag:
                    if config.generation_mode == "mock":
                        logger.info("Mock mode: waiting 5 seconds before next episode")
                        await asyncio.sleep(5)
                    else:
                        wait_time = config.scenes_per_episode * config.scene_generation_interval_minutes * 60
                        logger.info(f"Waiting {wait_time//60} minutes until next episode...")

                        for _ in range(wait_time):
                            if shutdown_flag:
                                break
                            await asyncio.sleep(1)

        finally:
            logger.info("Shutting down orchestrator...")
            await canon.update_series_state(system_status="idle")
            await db.disconnect()
            logger.info("Shutdown complete")


async def main():
    """Entry point."""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    orchestrator = Orchestrator()
    await orchestrator.run()


if __name__ == "__main__":
    print("=" * 60)
    print("  AniGen - Simple Mode (SQLite)")
    print("=" * 60)
    print()
    print("Using SQLite database - no PostgreSQL needed!")
    print("Press Ctrl+C to stop")
    print()

    asyncio.run(main())
