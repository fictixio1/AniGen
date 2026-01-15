"""Episode lifecycle management."""

import logging
from typing import Dict, Optional
from datetime import datetime
from decimal import Decimal
from database import db
from canon import canon

logger = logging.getLogger(__name__)


class EpisodeManager:
    """Manages episode and scene lifecycle."""

    async def start_episode(self, episode_number: int, director_plan: str, episode_summary: str) -> int:
        """
        Create a new episode record, or return existing episode if it already exists.

        Returns:
            episode_id: Database ID of the created or existing episode
        """
        # Check if episode already exists
        existing = await db.fetchrow("""
            SELECT id FROM episodes WHERE episode_number = $1
        """, episode_number)

        if existing:
            episode_id = existing['id']
            logger.warning(f"Episode {episode_number} already exists (ID: {episode_id}), reusing it")
            return episode_id

        # Create new episode
        episode_id = await db.fetchval("""
            INSERT INTO episodes (
                episode_number,
                director_plan,
                episode_arc_summary,
                generation_started_at
            ) VALUES ($1, $2, $3, $4)
            RETURNING id
        """, episode_number, director_plan, episode_summary, datetime.now())

        logger.info(f"Started episode {episode_number} (ID: {episode_id})")

        # Update series state
        await canon.update_series_state(
            current_episode=episode_number,
            current_scene_in_episode=1,
            system_status="planning_episode"
        )

        return episode_id

    async def create_scene(
        self,
        episode_id: int,
        scene_number: int,
        scene_in_episode: int,
        video_prompt: str,
        narrative_summary: str,
        video_url: str = "",
        duration_seconds: int = 30
    ) -> int:
        """
        Create a new scene record, or return existing scene if it already exists.

        Returns:
            scene_id: Database ID of the created or existing scene
        """
        # Check if scene already exists
        existing = await db.fetchrow("""
            SELECT id FROM scenes WHERE scene_number = $1
        """, scene_number)

        if existing:
            scene_id = existing['id']
            logger.warning(f"Scene {scene_number} already exists (ID: {scene_id}), reusing it")
            return scene_id

        # Create new scene
        scene_id = await db.fetchval("""
            INSERT INTO scenes (
                scene_number,
                episode_id,
                scene_in_episode,
                video_url,
                duration_seconds,
                video_prompt,
                narrative_summary,
                generation_started_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        """,
            scene_number,
            episode_id,
            scene_in_episode,
            video_url,
            duration_seconds,
            video_prompt,
            narrative_summary,
            datetime.now()
        )

        logger.info(f"Created scene {scene_number} (episode scene {scene_in_episode})")

        # Update series state
        await canon.update_series_state(
            current_scene_in_episode=scene_in_episode,
            system_status="generating_scene"
        )

        return scene_id

    async def complete_scene(
        self,
        scene_id: int,
        video_url: str,
        cost_usd: Decimal,
        retry_count: int = 0
    ):
        """Mark a scene as completed."""
        await db.execute("""
            UPDATE scenes
            SET video_url = $1,
                generation_cost_usd = $2,
                retry_count = $3,
                generation_completed_at = $4
            WHERE id = $5
        """, video_url, cost_usd, retry_count, datetime.now(), scene_id)

        # Update total scenes count
        state = await canon.get_series_state()
        await canon.update_series_state(total_scenes=state["total_scenes"] + 1)

        logger.info(f"Completed scene {scene_id} (cost: ${cost_usd})")

    async def complete_episode(self, episode_id: int):
        """Mark an episode as completed."""
        # Calculate total cost from all scenes
        total_cost = await db.fetchval("""
            SELECT COALESCE(SUM(generation_cost_usd), 0)
            FROM scenes
            WHERE episode_id = $1
        """, episode_id)

        await db.execute("""
            UPDATE episodes
            SET generation_completed_at = $1,
                total_cost_usd = $2
            WHERE id = $3
        """, datetime.now(), total_cost, episode_id)

        # Update series state
        state = await canon.get_series_state()
        await canon.update_series_state(
            total_episodes=state["total_episodes"] + 1,
            current_scene_in_episode=1,
            system_status="idle"
        )

        logger.info(f"Completed episode {episode_id} (total cost: ${total_cost})")

    async def get_episode(self, episode_number: int) -> Optional[Dict]:
        """Get episode by number."""
        row = await db.fetchrow("""
            SELECT * FROM episodes WHERE episode_number = $1
        """, episode_number)

        if not row:
            return None

        return dict(row)

    async def get_episode_scenes(self, episode_id: int) -> list[Dict]:
        """Get all scenes for an episode."""
        rows = await db.fetch("""
            SELECT * FROM scenes
            WHERE episode_id = $1
            ORDER BY scene_in_episode ASC
        """, episode_id)

        return [dict(row) for row in rows]

    async def log_generation_event(
        self,
        scene_number: Optional[int],
        level: str,
        component: str,
        message: str,
        error_details: Optional[str] = None
    ):
        """Log a generation event."""
        await db.execute("""
            INSERT INTO generation_logs (scene_number, log_level, component, message, error_details)
            VALUES ($1, $2, $3, $4, $5)
        """, scene_number, level, component, message, error_details)


# Global episode manager instance
episode_manager = EpisodeManager()
