"""Run AniGen system with Web UI."""

import asyncio
import subprocess
import sys
import signal
import logging

logger = logging.getLogger(__name__)

# Processes to manage
processes = []


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info("Shutting down all processes...")
    for proc in processes:
        proc.terminate()
    sys.exit(0)


async def main():
    """Run both the orchestrator and web UI."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("=" * 60)
    print("  AniGen - Starting System with Web UI")
    print("=" * 60)
    print()
    print("Starting components:")
    print("  [1] Orchestrator (episode generation)")
    print("  [2] Web UI (http://localhost:8000)")
    print()
    print("Press Ctrl+C to stop all components")
    print("=" * 60)
    print()

    # Start orchestrator
    print("[1/2] Starting orchestrator...")
    orchestrator = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    processes.append(orchestrator)
    print("✓ Orchestrator started")

    # Wait a moment for orchestrator to initialize
    await asyncio.sleep(2)

    # Start web UI
    print("[2/2] Starting web UI...")
    web_ui = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    processes.append(web_ui)
    print("✓ Web UI started at http://localhost:8000")
    print()
    print("=" * 60)
    print("  System Running!")
    print("=" * 60)
    print()
    print("🌐 Open your browser: http://localhost:8000")
    print("📊 Episodes will appear as they're generated")
    print("⚡ Mock mode: New episode every 5 seconds")
    print()
    print("Logs:")
    print("-" * 60)

    # Stream logs from both processes
    try:
        while True:
            # Read orchestrator output
            line = orchestrator.stdout.readline()
            if line:
                print(f"[ORCHESTRATOR] {line.strip()}")

            # Read web UI output
            line = web_ui.stdout.readline()
            if line:
                print(f"[WEB_UI] {line.strip()}")

            # Check if processes are still running
            if orchestrator.poll() is not None:
                print("Orchestrator process ended")
                break
            if web_ui.poll() is not None:
                print("Web UI process ended")
                break

            await asyncio.sleep(0.1)

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        for proc in processes:
            proc.terminate()
        print("All processes stopped")


if __name__ == "__main__":
    asyncio.run(main())
