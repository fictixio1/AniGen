"""Cleanup script to remove incomplete episodes and reset series state."""
import asyncio
import sys
from database import db
from config import config

async def cleanup_episode(episode_number: int):
    """Remove an episode and its scenes from the database."""
    try:
        await db.connect()

        # Get episode ID
        episode = await db.fetchrow(
            "SELECT id FROM episodes WHERE episode_number = $1",
            episode_number
        )

        if not episode:
            print(f"Episode {episode_number} not found in database")
            return

        episode_id = episode['id']

        # Delete scenes
        deleted_scenes = await db.execute(
            "DELETE FROM scenes WHERE episode_id = $1",
            episode_id
        )
        print(f"Deleted scenes for episode {episode_number}: {deleted_scenes}")

        # Delete episode
        deleted_episode = await db.execute(
            "DELETE FROM episodes WHERE id = $1",
            episode_id
        )
        print(f"Deleted episode {episode_number}: {deleted_episode}")

        # Reset series_state to start from this episode again
        await db.execute("""
            UPDATE series_state
            SET current_episode = $1,
                current_scene_in_episode = 1,
                system_status = 'idle'
            WHERE id = 1
        """, episode_number)
        print(f"Reset series_state to episode {episode_number}")

        print("\nCleanup complete! You can now restart the worker service.")

    except Exception as e:
        print(f"Error during cleanup: {e}")
        raise
    finally:
        await db.disconnect()

if __name__ == "__main__":
    episode_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    print(f"Cleaning up episode {episode_num}...")
    print(f"Using database: {config.database_url}")
    asyncio.run(cleanup_episode(episode_num))
