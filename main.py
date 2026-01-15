"""Main orchestration loop for infinite anime generation."""
# Ready for generation with Anthropic credits

import asyncio
import logging
import signal
import sys
from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from config import config
from database import db
from canon import canon
from episode_manager import episode_manager
from director import Director
from generators.video import VideoGenerator, MockVideoGenerator
from generators.character import CharacterImageGenerator, MockCharacterImageGenerator

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_flag = False


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    global shutdown_flag
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_flag = True


class MockDirector:
    """Mock Director for Phase 1 testing."""

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
    """Mock video generator for Phase 1 testing."""

    async def generate_video(self, prompt: str, duration: int) -> Dict:
        """Simulate video generation."""
        logger.info(f"Generating {duration}s video: {prompt[:50]}...")

        # Simulate generation time (instant for testing)
        await asyncio.sleep(0.1)

        return {
            "video_url": f"mock://video/{datetime.now().timestamp()}.mp4",
            "duration": duration,
            "cost": Decimal("4.50")
        }


class Orchestrator:
    """Main orchestration loop."""

    def __init__(self):
        # Use real or mock implementations based on GENERATION_MODE
        if config.generation_mode == "real":
            logger.info("Initializing REAL Director (Claude Opus 4.5), Video Generator (Luma AI Dream Machine), and Character Generator (DALL-E 3)")
            self.director = Director()
            self.video_generator = VideoGenerator()
            self.character_generator = CharacterImageGenerator()
        else:
            logger.info("Initializing MOCK Director, Video Generator, and Character Generator")
            self.director = MockDirector()
            self.video_generator = MockVideoGenerator()
            self.character_generator = MockCharacterImageGenerator()

    async def generate_episode(self):
        """Generate one complete episode (6 scenes)."""
        try:
            # Get current state
            state = await canon.get_series_state()
            episode_number = state["current_episode"]

            logger.info(f"\n{'='*60}")
            logger.info(f"Starting Episode {episode_number}")
            logger.info(f"{'='*60}")

            # Update status to planning
            await canon.update_series_state(system_status="planning_episode")

            # Step 1: Director plans the full episode
            context = await canon.build_director_context()
            episode_plan = await self.director.plan_episode(episode_number, context)

            # Log the plan
            await episode_manager.log_generation_event(
                scene_number=None,
                level="INFO",
                component="director",
                message=f"Planned episode {episode_number}: {episode_plan['episode_summary']}"
            )

            # Step 1.5: Generate character images for any new characters
            if episode_plan.get("new_characters"):
                logger.info(f"Generating images for {len(episode_plan['new_characters'])} new character(s)")

                for char_spec in episode_plan["new_characters"]:
                    try:
                        # Generate character image
                        char_result = await self.character_generator.generate_character_image(
                            character_name=char_spec["name"],
                            character_description=char_spec["description"]
                        )

                        # Store character in database
                        char_id = await canon.create_character(
                            name=char_spec["name"],
                            description=char_spec["description"],
                            image_url=char_result["image_url"],
                            role=char_spec.get("role", "supporting")
                        )

                        logger.info(f"✓ Character created: {char_spec['name']} (ID: {char_id})")

                    except Exception as e:
                        logger.error(f"Failed to generate character {char_spec['name']}: {e}")
                        # Continue anyway - character creation is not critical for episode generation

            # Create episode record
            episode_id = await episode_manager.start_episode(
                episode_number=episode_number,
                director_plan=str(episode_plan),
                episode_summary=episode_plan["episode_summary"]
            )

            # Step 2: Generate each scene sequentially
            global_scene_number = state["total_scenes"] + 1

            for scene_plan in episode_plan["scenes"]:
                if shutdown_flag:
                    logger.info("Shutdown requested, stopping episode generation")
                    return

                scene_in_episode = scene_plan["scene_in_episode"]
                logger.info(f"\nGenerating Scene {scene_in_episode}/6 (Global #{global_scene_number})")

                # Create scene record
                scene_id = await episode_manager.create_scene(
                    episode_id=episode_id,
                    scene_number=global_scene_number,
                    scene_in_episode=scene_in_episode,
                    video_prompt=scene_plan["video_prompt"],
                    narrative_summary=scene_plan["narrative_summary"],
                    duration_seconds=config.scene_duration_seconds
                )

                # Generate video
                video_result = await self.video_generator.generate_video(
                    prompt=scene_plan["video_prompt"],
                    duration=config.scene_duration_seconds
                )

                # Complete scene
                await episode_manager.complete_scene(
                    scene_id=scene_id,
                    video_url=video_result["video_url"],
                    cost_usd=video_result["cost"],
                    retry_count=0
                )

                logger.info(f"✓ Scene {scene_in_episode} completed: {video_result['video_url']}")

                global_scene_number += 1

                # Wait for scene interval (skip for mock mode or last scene)
                if scene_in_episode < config.scenes_per_episode and not shutdown_flag:
                    wait_seconds = config.scene_generation_interval_minutes * 60
                    logger.info(f"Waiting {config.scene_generation_interval_minutes} minutes until next scene...")

                    # Break wait into 1-second chunks to check shutdown flag
                    for _ in range(wait_seconds):
                        if shutdown_flag:
                            break
                        await asyncio.sleep(1)

            # Step 3: Complete episode
            if not shutdown_flag:
                await episode_manager.complete_episode(episode_id)

                # Get final episode stats
                episode = await episode_manager.get_episode(episode_number)
                logger.info(f"\n{'='*60}")
                logger.info(f"Episode {episode_number} Complete!")
                logger.info(f"Total Cost: ${episode['total_cost_usd']}")
                logger.info(f"Duration: {episode['total_duration_seconds']}s")
                logger.info(f"{'='*60}\n")

                # Increment episode counter for next iteration
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
        logger.info(f"Scenes per episode: {config.scenes_per_episode}")
        logger.info(f"Scene interval: {config.scene_generation_interval_minutes} minutes")

        # Connect to database
        await db.connect()

        try:
            while not shutdown_flag:
                await self.generate_episode()

                if not shutdown_flag:
                    # In mock mode, reduce wait time for testing
                    if config.generation_mode == "mock":
                        logger.info("Mock mode: waiting 5 seconds before next episode")
                        await asyncio.sleep(5)
                    else:
                        # Wait until next episode cycle (60 minutes total)
                        wait_time = config.scenes_per_episode * config.scene_generation_interval_minutes * 60
                        logger.info(f"Waiting {wait_time//60} minutes until next episode...")

                        for _ in range(wait_time):
                            if shutdown_flag:
                                break
                            await asyncio.sleep(1)

        finally:
            # Cleanup
            logger.info("Shutting down orchestrator...")
            await canon.update_series_state(system_status="idle")
            await db.disconnect()
            logger.info("Shutdown complete")


async def main():
    """Entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run orchestrator
    orchestrator = Orchestrator()
    await orchestrator.run()


if __name__ == "__main__":
    asyncio.run(main())
