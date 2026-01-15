"""API routes for AniGen web interface."""

from fastapi import APIRouter
from typing import List, Optional
from database import db

router = APIRouter()


@router.get("/api/episodes")
async def get_episodes(limit: int = 20, offset: int = 0):
    """Get list of episodes."""
    episodes = await db.fetch("""
        SELECT
            e.*,
            COUNT(s.id) as scene_count,
            COUNT(CASE WHEN s.generation_completed_at IS NOT NULL THEN 1 END) as completed_scenes
        FROM episodes e
        LEFT JOIN scenes s ON s.episode_id = e.id
        GROUP BY e.id
        ORDER BY e.episode_number DESC
        LIMIT $1 OFFSET $2
    """, limit, offset)

    total = await db.fetchval("SELECT COUNT(*) FROM episodes")

    return {
        "episodes": [dict(ep) for ep in episodes],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/api/episodes/{episode_number}")
async def get_episode(episode_number: int):
    """Get episode details with all scenes."""
    episode = await db.fetchrow("""
        SELECT * FROM episodes WHERE episode_number = $1
    """, episode_number)

    if not episode:
        return {"error": "Episode not found"}, 404

    scenes = await db.fetch("""
        SELECT * FROM scenes
        WHERE episode_id = $1
        ORDER BY scene_in_episode ASC
    """, episode["id"])

    return {
        "episode": dict(episode),
        "scenes": [dict(scene) for scene in scenes]
    }


@router.get("/api/scenes")
async def get_scenes(limit: int = 50, offset: int = 0):
    """Get list of scenes."""
    scenes = await db.fetch("""
        SELECT s.*, e.episode_number
        FROM scenes s
        JOIN episodes e ON s.episode_id = e.id
        ORDER BY s.scene_number DESC
        LIMIT $1 OFFSET $2
    """, limit, offset)

    total = await db.fetchval("SELECT COUNT(*) FROM scenes")

    return {
        "scenes": [dict(scene) for scene in scenes],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/api/characters")
async def get_characters():
    """Get all characters."""
    characters = await db.fetch("""
        SELECT * FROM characters ORDER BY created_at ASC
    """)

    return {
        "characters": [dict(char) for char in characters]
    }


@router.get("/api/series-info")
async def get_series_info():
    """Get series state and statistics."""
    state = await db.fetchrow("SELECT * FROM series_state WHERE id = 1")

    total_cost = await db.fetchval("""
        SELECT COALESCE(SUM(total_cost_usd), 0) FROM episodes
        WHERE generation_completed_at IS NOT NULL
    """)

    recent_episodes = await db.fetch("""
        SELECT episode_number, episode_arc_summary, total_cost_usd, generation_completed_at
        FROM episodes
        WHERE generation_completed_at IS NOT NULL
        ORDER BY episode_number DESC
        LIMIT 5
    """)

    return {
        "state": dict(state) if state else {},
        "total_cost": float(total_cost),
        "recent_episodes": [dict(ep) for ep in recent_episodes]
    }


@router.get("/api/logs")
async def get_logs(limit: int = 100, level: Optional[str] = None):
    """Get generation logs."""
    if level:
        logs = await db.fetch("""
            SELECT * FROM generation_logs
            WHERE log_level = $1
            ORDER BY created_at DESC
            LIMIT $2
        """, level.upper(), limit)
    else:
        logs = await db.fetch("""
            SELECT * FROM generation_logs
            ORDER BY created_at DESC
            LIMIT $1
        """, limit)

    return {
        "logs": [dict(log) for log in logs],
        "limit": limit
    }
