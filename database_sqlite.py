"""SQLite database connection - no server needed."""

import aiosqlite
import logging
from typing import Optional
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class Database:
    """SQLite connection manager."""

    def __init__(self, db_path: str = "anigen.db"):
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Create database connection."""
        if self.conn is None:
            logger.info(f"Connecting to SQLite database: {self.db_path}")
            self.conn = await aiosqlite.connect(self.db_path)
            self.conn.row_factory = aiosqlite.Row
            await self._init_schema()
            logger.info("Database connection established")

    async def _init_schema(self):
        """Initialize database schema."""
        schema = """
        CREATE TABLE IF NOT EXISTS series_state (
            id INTEGER PRIMARY KEY,
            current_episode INTEGER NOT NULL DEFAULT 1,
            current_scene_in_episode INTEGER NOT NULL DEFAULT 1,
            total_scenes INTEGER NOT NULL DEFAULT 0,
            total_episodes INTEGER NOT NULL DEFAULT 0,
            last_generated_at TEXT,
            system_status TEXT DEFAULT 'idle',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS characters (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            image_url TEXT NOT NULL,
            image_version INTEGER DEFAULT 1,
            canonical_state TEXT,
            first_appearance_scene INTEGER,
            last_appearance_scene INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            episode_number INTEGER UNIQUE NOT NULL,
            total_duration_seconds INTEGER DEFAULT 180,
            director_plan TEXT NOT NULL,
            episode_arc_summary TEXT,
            generation_started_at TEXT,
            generation_completed_at TEXT,
            total_cost_usd REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS scenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scene_number INTEGER UNIQUE NOT NULL,
            episode_id INTEGER,
            scene_in_episode INTEGER NOT NULL,
            video_url TEXT NOT NULL,
            duration_seconds INTEGER DEFAULT 30,
            video_prompt TEXT NOT NULL,
            narrative_summary TEXT NOT NULL,
            generation_started_at TEXT,
            generation_completed_at TEXT,
            generation_cost_usd REAL,
            retry_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS narrative_context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scene_id INTEGER,
            context_type TEXT,
            content TEXT NOT NULL,
            priority INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS generation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scene_number INTEGER,
            log_level TEXT,
            component TEXT,
            message TEXT NOT NULL,
            error_details TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_episodes_episode_number ON episodes(episode_number DESC);
        CREATE INDEX IF NOT EXISTS idx_scenes_scene_number ON scenes(scene_number DESC);
        CREATE INDEX IF NOT EXISTS idx_scenes_episode ON scenes(episode_id);
        CREATE INDEX IF NOT EXISTS idx_narrative_context_scene ON narrative_context(scene_id);
        CREATE INDEX IF NOT EXISTS idx_generation_logs_scene ON generation_logs(scene_number);

        INSERT OR IGNORE INTO series_state (id, current_episode, current_scene_in_episode, total_scenes, total_episodes)
        VALUES (1, 1, 1, 0, 0);
        """

        await self.conn.executescript(schema)
        await self.conn.commit()

    async def disconnect(self):
        """Close database connection."""
        if self.conn:
            await self.conn.close()
            logger.info("Database connection closed")
            self.conn = None

    @asynccontextmanager
    async def transaction(self):
        """Context manager for transactions."""
        if not self.conn:
            raise RuntimeError("Database not connected")

        try:
            yield self.conn
            await self.conn.commit()
        except Exception:
            await self.conn.rollback()
            raise

    async def execute(self, query: str, *args):
        """Execute a query without returning results."""
        if not self.conn:
            raise RuntimeError("Database not connected")
        await self.conn.execute(query, args)
        await self.conn.commit()

    async def fetch(self, query: str, *args):
        """Execute a query and return all results."""
        if not self.conn:
            raise RuntimeError("Database not connected")
        cursor = await self.conn.execute(query, args)
        return await cursor.fetchall()

    async def fetchrow(self, query: str, *args):
        """Execute a query and return a single row."""
        if not self.conn:
            raise RuntimeError("Database not connected")
        cursor = await self.conn.execute(query, args)
        return await cursor.fetchone()

    async def fetchval(self, query: str, *args):
        """Execute a query and return a single value."""
        if not self.conn:
            raise RuntimeError("Database not connected")
        cursor = await self.conn.execute(query, args)
        row = await cursor.fetchone()
        return row[0] if row else None


# Global database instance
db = Database()
