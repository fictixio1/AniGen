"""Ultra simple version - minimal dependencies."""

import asyncio
import aiosqlite
import logging
import signal
from datetime import datetime
from decimal import Decimal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

shutdown_flag = False


def signal_handler(signum, frame):
    global shutdown_flag
    logger.info("Shutdown requested...")
    shutdown_flag = True


class Database:
    """SQLite database manager."""

    def __init__(self):
        self.conn = None

    async def connect(self):
        """Connect to database."""
        logger.info("Connecting to database...")
        self.conn = await aiosqlite.connect("anigen.db")
        self.conn.row_factory = aiosqlite.Row
        await self._init_schema()
        logger.info("✓ Database ready")

    async def _init_schema(self):
        """Create tables."""
        await self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                episode_number INTEGER UNIQUE NOT NULL,
                summary TEXT,
                total_cost REAL,
                completed_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS scenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scene_number INTEGER UNIQUE NOT NULL,
                episode_id INTEGER,
                scene_in_episode INTEGER,
                video_url TEXT,
                narrative TEXT,
                cost REAL,
                completed_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            INSERT OR IGNORE INTO episodes (episode_number, summary, total_cost)
            VALUES (0, 'Initialization', 0.0);
        """)
        await self.conn.commit()

    async def disconnect(self):
        """Close connection."""
        if self.conn:
            await self.conn.close()

    async def create_episode(self, episode_number, summary):
        """Create new episode."""
        cursor = await self.conn.execute(
            "INSERT INTO episodes (episode_number, summary) VALUES (?, ?)",
            (episode_number, summary)
        )
        await self.conn.commit()
        return cursor.lastrowid

    async def create_scene(self, episode_id, scene_number, scene_in_episode, narrative, video_url, cost):
        """Create new scene."""
        await self.conn.execute(
            "INSERT INTO scenes (episode_id, scene_number, scene_in_episode, narrative, video_url, cost, completed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (episode_id, scene_number, scene_in_episode, narrative, video_url, cost, datetime.now().isoformat())
        )
        await self.conn.commit()

    async def complete_episode(self, episode_id, total_cost):
        """Mark episode complete."""
        await self.conn.execute(
            "UPDATE episodes SET total_cost = ?, completed_at = ? WHERE id = ?",
            (total_cost, datetime.now().isoformat(), episode_id)
        )
        await self.conn.commit()

    async def get_episode_count(self):
        """Get total episodes."""
        cursor = await self.conn.execute("SELECT COUNT(*) FROM episodes WHERE episode_number > 0")
        row = await cursor.fetchone()
        return row[0] if row else 0


class MockDirector:
    """Mock episode planner."""

    def plan_episode(self, episode_number):
        """Plan 6 scenes."""
        logger.info(f"Planning Episode {episode_number}")
        scenes = []
        for i in range(1, 7):
            scenes.append({
                "scene_in_episode": i,
                "narrative": f"Episode {episode_number}, Scene {i}: Characters continue their journey",
                "video_prompt": f"Anime scene {i} with action"
            })
        return {
            "summary": f"Episode {episode_number}: A thrilling continuation",
            "scenes": scenes
        }


class MockVideoGenerator:
    """Mock video generator."""

    async def generate(self, prompt):
        """Generate mock video."""
        await asyncio.sleep(0.1)
        return {
            "url": f"mock://video/{datetime.now().timestamp()}.mp4",
            "cost": 4.50
        }


class Orchestrator:
    """Main system."""

    def __init__(self):
        self.db = Database()
        self.director = MockDirector()
        self.video_gen = MockVideoGenerator()

    async def generate_episode(self, episode_number):
        """Generate one episode."""
        logger.info(f"\n{'='*60}")
        logger.info(f"EPISODE {episode_number}")
        logger.info(f"{'='*60}")

        # Plan episode
        plan = self.director.plan_episode(episode_number)
        episode_id = await self.db.create_episode(episode_number, plan["summary"])

        # Generate scenes
        global_scene = (episode_number - 1) * 6 + 1
        total_cost = 0

        for scene_plan in plan["scenes"]:
            if shutdown_flag:
                return

            scene_num = scene_plan["scene_in_episode"]
            logger.info(f"\n  Scene {scene_num}/6 (Global #{global_scene})")

            # Generate video
            video = await self.video_gen.generate(scene_plan["video_prompt"])

            # Save scene
            await self.db.create_scene(
                episode_id=episode_id,
                scene_number=global_scene,
                scene_in_episode=scene_num,
                narrative=scene_plan["narrative"],
                video_url=video["url"],
                cost=video["cost"]
            )

            logger.info(f"  ✓ {video['url']}")
            total_cost += video["cost"]
            global_scene += 1

            # Wait between scenes
            if scene_num < 6 and not shutdown_flag:
                await asyncio.sleep(5)  # 5 seconds in mock mode

        # Complete episode
        await self.db.complete_episode(episode_id, total_cost)

        logger.info(f"\n{'='*60}")
        logger.info(f"✓ Episode {episode_number} Complete!")
        logger.info(f"  Cost: ${total_cost:.2f}")
        logger.info(f"{'='*60}\n")

    async def run(self):
        """Main loop."""
        await self.db.connect()

        try:
            episode_number = await self.db.get_episode_count() + 1

            while not shutdown_flag:
                await self.generate_episode(episode_number)
                episode_number += 1

                if not shutdown_flag:
                    logger.info("Waiting 5 seconds before next episode...")
                    await asyncio.sleep(5)

        finally:
            await self.db.disconnect()
            logger.info("Shutdown complete")


async def main():
    signal.signal(signal.SIGINT, signal_handler)

    print("=" * 60)
    print("  AniGen - Ultra Simple Mode")
    print("=" * 60)
    print()
    print("Database: SQLite (anigen.db)")
    print("Episodes: 6 scenes each, generated every 5 seconds")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    orchestrator = Orchestrator()
    await orchestrator.run()


if __name__ == "__main__":
    asyncio.run(main())
