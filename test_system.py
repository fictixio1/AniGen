"""Test script to verify AniGen system is working correctly."""

import asyncio
import sys
from datetime import datetime


async def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        from config import config
        from database import db
        from canon import canon
        from episode_manager import episode_manager
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


async def test_database_connection():
    """Test database connection."""
    print("\nTesting database connection...")
    try:
        from database import db
        await db.connect()
        result = await db.fetchval("SELECT 1")
        if result == 1:
            print("✓ Database connection successful")
            return True
        else:
            print("✗ Database returned unexpected value")
            return False
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("  Make sure PostgreSQL is running")
        print("  Try: docker compose up -d postgres")
        return False
    finally:
        await db.disconnect()


async def test_database_schema():
    """Test that all required tables exist."""
    print("\nTesting database schema...")
    try:
        from database import db
        await db.connect()

        tables = ['series_state', 'episodes', 'scenes', 'characters', 'narrative_context', 'generation_logs']
        for table in tables:
            count = await db.fetchval(f"SELECT COUNT(*) FROM {table}")
            print(f"  ✓ Table '{table}' exists (rows: {count})")

        return True
    except Exception as e:
        print(f"✗ Schema test failed: {e}")
        print("  Run: psql -U anigen_user -d anigen -f schemas/database_schema.sql")
        return False
    finally:
        await db.disconnect()


async def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")
    try:
        from config import config

        print(f"  ✓ Generation mode: {config.generation_mode}")
        print(f"  ✓ Scenes per episode: {config.scenes_per_episode}")
        print(f"  ✓ Scene interval: {config.scene_generation_interval_minutes} min")
        print(f"  ✓ Database URL: {config.database_url[:50]}...")

        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


async def test_episode_generation():
    """Test creating a mock episode."""
    print("\nTesting episode generation...")
    try:
        from database import db
        from episode_manager import episode_manager
        from decimal import Decimal

        await db.connect()

        # Create test episode
        episode_id = await episode_manager.start_episode(
            episode_number=9999,
            director_plan="Test episode plan",
            episode_summary="Test episode summary"
        )
        print(f"  ✓ Created test episode (ID: {episode_id})")

        # Create test scene
        scene_id = await episode_manager.create_scene(
            episode_id=episode_id,
            scene_number=99999,
            scene_in_episode=1,
            video_prompt="Test video prompt",
            narrative_summary="Test narrative",
            video_url="test://video.mp4"
        )
        print(f"  ✓ Created test scene (ID: {scene_id})")

        # Complete scene
        await episode_manager.complete_scene(
            scene_id=scene_id,
            video_url="test://video.mp4",
            cost_usd=Decimal("4.50")
        )
        print(f"  ✓ Completed test scene")

        # Complete episode
        await episode_manager.complete_episode(episode_id)
        print(f"  ✓ Completed test episode")

        # Clean up test data
        await db.execute("DELETE FROM episodes WHERE episode_number = 9999")
        print(f"  ✓ Cleaned up test data")

        return True
    except Exception as e:
        print(f"✗ Episode generation test failed: {e}")
        return False
    finally:
        await db.disconnect()


async def test_web_api():
    """Test that FastAPI can be imported and configured."""
    print("\nTesting Web API...")
    try:
        from api.main import app
        print(f"  ✓ FastAPI app created")
        print(f"  ✓ Title: {app.title}")
        print(f"  ✓ Version: {app.version}")
        return True
    except Exception as e:
        print(f"✗ Web API test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("  AniGen System Test")
    print("=" * 60)
    print()

    results = []

    # Run tests
    results.append(("Imports", await test_imports()))
    results.append(("Configuration", await test_configuration()))
    results.append(("Database Connection", await test_database_connection()))
    results.append(("Database Schema", await test_database_schema()))
    results.append(("Episode Generation", await test_episode_generation()))
    results.append(("Web API", await test_web_api()))

    # Summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print()
        print("🎉 All tests passed! System is ready to run.")
        print()
        print("Next steps:")
        print("  1. Run the system: python run_with_ui.py")
        print("  2. Open browser: http://localhost:8000")
        print()
        return 0
    else:
        print()
        print("⚠️  Some tests failed. Please fix the issues above.")
        print()
        print("Common fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Start database: docker compose up -d postgres")
        print("  - Initialize schema: psql -U anigen_user -d anigen -f schemas/database_schema.sql")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
