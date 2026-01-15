"""Video generation using Runway Gen-3 Alpha."""

import logging
import asyncio
import time
import httpx
from typing import Dict
from decimal import Decimal

from config import config

logger = logging.getLogger(__name__)


class VideoGenerator:
    """Runway Gen-3 Alpha video generator."""

    def __init__(self):
        self.api_key = config.runway_api_key if hasattr(config, 'runway_api_key') else config.google_ai_api_key
        self.base_url = "https://api.runwayml.com/v1"

    async def generate_video(self, prompt: str, duration: int = 30) -> Dict:
        """
        Generate a video using Runway Gen-3 Alpha.

        Args:
            prompt: Video description/prompt
            duration: Video duration in seconds (default 30, max 10 for Gen-3)

        Returns:
            Dict with video_url, duration, and cost
        """
        # Runway Gen-3 maxes out at 10 seconds per generation
        # We'll generate a 5-second clip for now
        actual_duration = min(duration, 5)

        logger.info(f"Generating {actual_duration}s video with Runway Gen-3 Alpha")
        logger.info(f"Prompt: {prompt[:100]}...")

        try:
            start_time = time.time()

            # Enhance prompt for anime style
            enhanced_prompt = self._enhance_prompt_for_anime(prompt)

            # Generate video using Runway API
            response = await self._call_runway_api(enhanced_prompt, actual_duration)

            generation_time = time.time() - start_time

            # Calculate cost: ~$0.05 per second for Gen-3 Alpha
            cost = Decimal(str(actual_duration)) * Decimal("0.05")

            result = {
                "video_url": response["video_url"],
                "duration": actual_duration,
                "cost": cost,
                "generation_time": generation_time
            }

            logger.info(f"Video generated successfully in {generation_time:.1f}s (cost: ${cost})")
            logger.info(f"Video URL: {result['video_url']}")

            return result

        except Exception as e:
            logger.error(f"Error generating video with Runway: {e}")
            # Fall back to mock for development
            logger.warning("Falling back to mock video generation")
            return {
                "video_url": f"mock://video/{int(time.time())}.mp4",
                "duration": actual_duration,
                "cost": Decimal("0.25"),
                "generation_time": 0.1
            }

    async def _call_runway_api(self, prompt: str, duration: int) -> Dict:
        """
        Call Runway Gen-3 API for video generation.

        Docs: https://docs.runwayml.com/
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Start generation
        payload = {
            "promptText": prompt,
            "model": "gen3a_turbo",  # Fastest Gen-3 model
            "duration": duration,
            "ratio": "16:9",
            "watermark": False
        }

        async with httpx.AsyncClient(timeout=300.0) as client:
            # Submit generation request
            logger.info("Submitting video generation request to Runway...")
            response = await client.post(
                f"{self.base_url}/image_to_video",
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"Runway API error: {response.status_code} - {response.text}")

            data = response.json()
            task_id = data.get("id")

            if not task_id:
                raise Exception(f"No task ID returned from Runway: {data}")

            logger.info(f"Video generation started (task ID: {task_id})")

            # Poll for completion
            max_attempts = 60  # 5 minutes max
            for attempt in range(max_attempts):
                await asyncio.sleep(5)  # Check every 5 seconds

                status_response = await client.get(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=headers
                )

                if status_response.status_code != 200:
                    raise Exception(f"Status check failed: {status_response.status_code}")

                status_data = status_response.json()
                status = status_data.get("status")

                logger.info(f"Generation status: {status} (attempt {attempt + 1}/{max_attempts})")

                if status == "SUCCEEDED":
                    video_url = status_data.get("output", [None])[0]
                    if not video_url:
                        raise Exception("No video URL in response")

                    return {"video_url": video_url}

                elif status in ["FAILED", "CANCELLED"]:
                    error_msg = status_data.get("error", "Unknown error")
                    raise Exception(f"Generation failed: {error_msg}")

            # Timeout
            raise Exception("Video generation timed out after 5 minutes")

    def _enhance_prompt_for_anime(self, prompt: str) -> str:
        """Enhance the prompt to ensure anime-style video generation."""
        # If prompt already specifies anime style, don't duplicate
        if "anime" in prompt.lower() or "animated" in prompt.lower():
            return prompt

        # Add anime-specific enhancements
        enhanced = f"High-quality anime style animation: {prompt}. Japanese animation aesthetic, vibrant colors, expressive characters, cinematic composition."
        return enhanced


class MockVideoGenerator:
    """Mock video generator for testing without API calls."""

    async def generate_video(self, prompt: str, duration: int = 30) -> Dict:
        """Simulate video generation."""
        logger.info(f"[MOCK] Generating {duration}s video: {prompt[:50]}...")

        # Simulate generation time
        await asyncio.sleep(0.5)

        return {
            "video_url": f"mock://video/{int(time.time())}.mp4",
            "duration": duration,
            "cost": Decimal("0.25")
        }
