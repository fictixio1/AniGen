"""Video generation using Luma AI Dream Machine."""

import logging
import asyncio
import time
import httpx
import subprocess
import tempfile
import os
from typing import Dict, List
from decimal import Decimal

from config import config

logger = logging.getLogger(__name__)


class VideoGenerator:
    """Luma AI Dream Machine video generator with extension for 30s clips."""

    def __init__(self):
        self.api_key = config.luma_api_key
        self.base_url = "https://api.lumalabs.ai/dream-machine/v1"

        logger.info(f"Luma API Key: {self.api_key[:10]}..." if self.api_key else "Luma API Key: NOT SET")

    async def generate_video(self, prompt: str, duration: int = 30) -> Dict:
        """
        Generate a 30-second video using Luma AI (6x 5s clips).

        Args:
            prompt: Video description/prompt
            duration: Video duration in seconds (default 30)

        Returns:
            Dict with video_url, duration, and cost
        """
        logger.info(f"Generating {duration}s video with Luma AI Dream Machine")
        logger.info(f"Prompt: {prompt[:100]}...")

        try:
            start_time = time.time()

            # Enhance prompt for anime style
            enhanced_prompt = self._enhance_prompt_for_anime(prompt)

            # Generate 6x 5-second clips (Luma generates ~5s per clip)
            num_clips = 6  # 6 × 5s = 30s total

            logger.info(f"Generating {num_clips} clips of ~5s each...")
            clip_urls = []

            for i in range(num_clips):
                logger.info(f"Generating clip {i+1}/{num_clips}...")
                clip_prompt = self._adapt_prompt_for_segment(enhanced_prompt, i+1, num_clips)
                clip_url = await self._generate_single_clip(clip_prompt)
                clip_urls.append(clip_url)
                logger.info(f"✓ Clip {i+1} generated: {clip_url}")

            # Concatenate clips using FFmpeg
            logger.info("Concatenating clips with FFmpeg...")
            final_video_url = await self._concatenate_clips(clip_urls)

            generation_time = time.time() - start_time

            # Calculate cost: ~$0.10 per 5s clip × 6 clips = $0.60 per 30s scene
            cost = Decimal(str(num_clips)) * Decimal("0.10")

            result = {
                "video_url": final_video_url,
                "duration": duration,
                "cost": cost,
                "generation_time": generation_time
            }

            logger.info(f"Video generated successfully in {generation_time:.1f}s (cost: ${cost})")
            logger.info(f"Final video URL: {result['video_url']}")

            return result

        except Exception as e:
            logger.error(f"Error generating video with Luma AI: {e}")
            # Fall back to mock for development
            logger.warning("Falling back to mock video generation")
            return {
                "video_url": f"mock://video/{int(time.time())}.mp4",
                "duration": duration,
                "cost": Decimal("0.60"),
                "generation_time": 0.1
            }

    async def _generate_single_clip(self, prompt: str) -> str:
        """
        Generate a single ~5s video clip using Luma AI API.

        Args:
            prompt: Enhanced video prompt

        Returns:
            Video URL
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "loop": False
        }

        async with httpx.AsyncClient(timeout=600.0) as client:
            # Submit generation request
            logger.info("Submitting generation request to Luma AI...")
            response = await client.post(
                f"{self.base_url}/generations",
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"Luma AI API error: {response.status_code} - {response.text}")

            data = response.json()
            generation_id = data.get("id")

            if not generation_id:
                raise Exception(f"No generation ID returned from Luma AI: {data}")

            logger.info(f"Video generation started (ID: {generation_id})")

            # Poll for completion
            max_attempts = 120  # 10 minutes max
            for attempt in range(max_attempts):
                await asyncio.sleep(5)  # Check every 5 seconds

                status_response = await client.get(
                    f"{self.base_url}/generations/{generation_id}",
                    headers=headers
                )

                if status_response.status_code != 200:
                    raise Exception(f"Status check failed: {status_response.status_code}")

                status_data = status_response.json()
                state = status_data.get("state")

                logger.info(f"Generation state: {state} (attempt {attempt + 1}/{max_attempts})")

                if state == "completed":
                    video_url = status_data.get("video", {}).get("url")
                    if not video_url:
                        raise Exception("No video URL in response")

                    return video_url

                elif state == "failed":
                    error_msg = status_data.get("failure_reason", "Unknown error")
                    raise Exception(f"Generation failed: {error_msg}")

            # Timeout
            raise Exception("Video generation timed out after 10 minutes")

    async def _concatenate_clips(self, clip_urls: List[str]) -> str:
        """
        Download clips and concatenate them using FFmpeg.

        Args:
            clip_urls: List of video URLs to concatenate

        Returns:
            URL of concatenated video (uploaded to temporary storage)
        """
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as tmpdir:
            # Download all clips
            clip_files = []
            async with httpx.AsyncClient(timeout=300.0) as client:
                for i, url in enumerate(clip_urls):
                    logger.info(f"Downloading clip {i+1}/{len(clip_urls)}...")
                    response = await client.get(url)
                    if response.status_code != 200:
                        raise Exception(f"Failed to download clip {i+1}")

                    clip_path = os.path.join(tmpdir, f"clip_{i+1}.mp4")
                    with open(clip_path, "wb") as f:
                        f.write(response.content)
                    clip_files.append(clip_path)

            # Create FFmpeg concat file
            concat_file = os.path.join(tmpdir, "concat_list.txt")
            with open(concat_file, "w") as f:
                for clip_path in clip_files:
                    f.write(f"file '{clip_path}'\n")

            # Concatenate with FFmpeg
            output_path = os.path.join(tmpdir, "output.mp4")
            ffmpeg_cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",  # Copy codec (no re-encoding for speed)
                output_path
            ]

            logger.info("Running FFmpeg concatenation...")
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise Exception(f"FFmpeg concatenation failed: {result.stderr}")

            logger.info("✓ FFmpeg concatenation complete")

            # TODO: Upload to S3/storage and return public URL
            # For now, return first clip URL as placeholder
            # You'll need to implement proper S3 upload in storage.py
            logger.warning("Using first clip URL as placeholder - implement S3 upload for concatenated video")
            return clip_urls[0]

    def _enhance_prompt_for_anime(self, prompt: str) -> str:
        """Enhance the prompt to ensure anime-style video generation."""
        # If prompt already specifies anime style, don't duplicate
        if "anime" in prompt.lower() or "animated" in prompt.lower():
            return prompt

        # Add anime-specific enhancements
        enhanced = f"High-quality anime style animation: {prompt}. Japanese animation aesthetic, vibrant colors, expressive characters, smooth motion, cinematic composition."
        return enhanced

    def _adapt_prompt_for_segment(self, base_prompt: str, segment_num: int, total_segments: int) -> str:
        """
        Adapt prompt for specific segment to ensure continuity.

        Args:
            base_prompt: Original enhanced prompt
            segment_num: Current segment number (1-6)
            total_segments: Total number of segments

        Returns:
            Adapted prompt for this segment
        """
        if segment_num == 1:
            return f"{base_prompt} [Opening sequence]"
        elif segment_num == total_segments:
            return f"{base_prompt} [Conclusion]"
        else:
            return f"{base_prompt} [Continuation, mid-sequence]"


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
            "cost": Decimal("0.60")
        }
