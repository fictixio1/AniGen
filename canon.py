"""Canon memory management with PostgreSQL backend."""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from database import db

logger = logging.getLogger(__name__)


class CanonMemory:
    """Manages canon state in the database."""

    async def get_series_state(self) -> Dict:
        """Get current series state."""
        row = await db.fetchrow("SELECT * FROM series_state WHERE id = 1")
        if not row:
            raise RuntimeError("Series state not initialized")

        return {
            "current_episode": row["current_episode"],
            "current_scene_in_episode": row["current_scene_in_episode"],
            "total_scenes": row["total_scenes"],
            "total_episodes": row["total_episodes"],
            "last_generated_at": row["last_generated_at"],
            "system_status": row["system_status"]
        }

    async def update_series_state(
        self,
        current_episode: Optional[int] = None,
        current_scene_in_episode: Optional[int] = None,
        total_scenes: Optional[int] = None,
        total_episodes: Optional[int] = None,
        system_status: Optional[str] = None
    ):
        """Update series state."""
        updates = []
        values = []
        param_count = 1

        if current_episode is not None:
            updates.append(f"current_episode = ${param_count}")
            values.append(current_episode)
            param_count += 1

        if current_scene_in_episode is not None:
            updates.append(f"current_scene_in_episode = ${param_count}")
            values.append(current_scene_in_episode)
            param_count += 1

        if total_scenes is not None:
            updates.append(f"total_scenes = ${param_count}")
            values.append(total_scenes)
            param_count += 1

        if total_episodes is not None:
            updates.append(f"total_episodes = ${param_count}")
            values.append(total_episodes)
            param_count += 1

        if system_status is not None:
            updates.append(f"system_status = ${param_count}")
            values.append(system_status)
            param_count += 1

        if updates:
            updates.append(f"updated_at = ${param_count}")
            values.append(datetime.now())
            param_count += 1

            updates.append(f"last_generated_at = ${param_count}")
            values.append(datetime.now())

            query = f"UPDATE series_state SET {', '.join(updates)} WHERE id = 1"
            await db.execute(query, *values)
            logger.info(f"Updated series state: {updates}")

    async def get_recent_scenes(self, limit: int = 100) -> List[Dict]:
        """Get recent scenes for context."""
        rows = await db.fetch("""
            SELECT s.*, e.episode_number, e.episode_arc_summary
            FROM scenes s
            JOIN episodes e ON s.episode_id = e.id
            ORDER BY s.scene_number DESC
            LIMIT $1
        """, limit)

        return [
            {
                "scene_number": row["scene_number"],
                "episode_number": row["episode_number"],
                "scene_in_episode": row["scene_in_episode"],
                "narrative_summary": row["narrative_summary"],
                "video_prompt": row["video_prompt"],
                "episode_arc_summary": row["episode_arc_summary"]
            }
            for row in rows
        ]

    async def get_characters(self) -> List[Dict]:
        """Get all characters."""
        rows = await db.fetch("SELECT * FROM characters ORDER BY created_at")

        return [
            {
                "id": row["id"],
                "name": row["name"],
                "image_url": row["image_url"],
                "canonical_state": row["canonical_state"],
                "last_appearance_scene": row["last_appearance_scene"]
            }
            for row in rows
        ]

    async def create_character(
        self,
        name: str,
        description: str,
        image_url: str,
        role: str = "supporting"
    ) -> str:
        """
        Create a new character in the database.

        Returns:
            character_id: The database ID for the character
        """
        # Generate a unique character ID
        count = await db.fetchval("SELECT COUNT(*) FROM characters")
        char_id = f"char_{count + 1:03d}"

        # Get current scene number for first_appearance
        state = await self.get_series_state()
        current_scene = state["total_scenes"] + 1

        await db.execute("""
            INSERT INTO characters (id, name, image_url, canonical_state, first_appearance_scene, last_appearance_scene)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, char_id, name, image_url, description, current_scene, current_scene)

        logger.info(f"Created character: {name} (ID: {char_id})")
        return char_id

    async def get_narrative_context(self, limit: int = 20) -> List[Dict]:
        """Get recent narrative context."""
        rows = await db.fetch("""
            SELECT * FROM narrative_context
            ORDER BY priority DESC, created_at DESC
            LIMIT $1
        """, limit)

        return [
            {
                "context_type": row["context_type"],
                "content": row["content"],
                "priority": row["priority"]
            }
            for row in rows
        ]

    async def build_director_context(self) -> Dict:
        """Build complete context for Director model."""
        series_state = await self.get_series_state()
        recent_scenes = await self.get_recent_scenes(limit=100)
        characters_list = await self.get_characters()
        narrative_context = await self.get_narrative_context(limit=20)

        # Format characters for Director prompt
        characters_dict = {
            char["id"]: {
                "name": char["name"],
                "canonical_state": char["canonical_state"],
                "image_url": char["image_url"]
            }
            for char in characters_list
        }

        # Format recent events from scenes
        recent_events = [
            f"Scene {scene['scene_number']} (Ep {scene['episode_number']}, Scene {scene['scene_in_episode']}): {scene['narrative_summary']}"
            for scene in recent_scenes[-10:]  # Last 10 scenes
        ]

        # Extract open threads from narrative context
        open_threads = [
            ctx["content"]
            for ctx in narrative_context
            if ctx["context_type"] == "open_thread"
        ]

        return {
            "series_state": series_state,
            "characters": characters_dict,
            "recent_events": recent_events,
            "open_threads": open_threads,
            "current_arc": "Beginning"  # TODO: Track arcs properly
        }


# Global canon instance
canon = CanonMemory()
