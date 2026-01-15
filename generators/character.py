"""Character image generation using DALL-E 3."""

import logging
from typing import Dict, Optional
from decimal import Decimal
from openai import OpenAI

from config import config

logger = logging.getLogger(__name__)


class CharacterImageGenerator:
    """DALL-E 3 character image generator."""

    def __init__(self):
        self.client = OpenAI(api_key=config.openai_api_key)
        self.model = "dall-e-3"

    async def generate_character_image(
        self,
        character_name: str,
        character_description: str,
        style: str = "anime"
    ) -> Dict:
        """
        Generate a character reference image.

        Args:
            character_name: Name of the character
            character_description: Physical description and personality traits
            style: Art style (default: anime)

        Returns:
            Dict with image_url, cost, and prompt used
        """
        logger.info(f"Generating character image for: {character_name}")

        # Build the prompt
        prompt = self._build_character_prompt(character_name, character_description, style)

        try:
            # Generate image with DALL-E 3
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size="1024x1024",  # Standard size for character references
                quality="standard",  # "standard" or "hd" - standard is cheaper
                n=1
            )

            image_url = response.data[0].url

            # Cost calculation
            # DALL-E 3 pricing: $0.040 per standard 1024x1024 image
            cost = Decimal("0.040")

            result = {
                "image_url": image_url,
                "prompt": prompt,
                "cost": cost,
                "character_name": character_name
            }

            logger.info(f"Character image generated for {character_name} (cost: ${cost})")
            logger.info(f"Image URL: {image_url}")

            return result

        except Exception as e:
            logger.error(f"Error generating character image: {e}")
            raise

    def _build_character_prompt(
        self,
        character_name: str,
        description: str,
        style: str
    ) -> str:
        """Build an optimized prompt for character image generation."""

        # Base prompt for consistent anime style
        base_prompt = f"{style} character reference sheet, full body character design"

        # Character details
        character_prompt = f"{character_name}: {description}"

        # Style guidelines for consistency
        style_guidelines = [
            "professional character design",
            "clean white background",
            "front-facing pose",
            "full body visible",
            "high quality anime art style",
            "vibrant colors",
            "sharp details",
            "character reference for animation"
        ]

        # Combine all elements
        full_prompt = f"{base_prompt}. {character_prompt}. {', '.join(style_guidelines)}"

        # Ensure prompt is under DALL-E 3's limit (4000 chars)
        if len(full_prompt) > 3900:
            full_prompt = full_prompt[:3900] + "..."

        return full_prompt

    async def regenerate_character_image(
        self,
        character_id: str,
        character_name: str,
        new_description: str,
        reason: str = "appearance change"
    ) -> Dict:
        """
        Regenerate a character image (e.g., after injury, costume change).

        Args:
            character_id: Character database ID
            character_name: Character name
            new_description: Updated description
            reason: Why the image is being regenerated

        Returns:
            Dict with new image_url, cost, and metadata
        """
        logger.info(f"Regenerating character image for {character_name} (reason: {reason})")

        result = await self.generate_character_image(
            character_name=character_name,
            character_description=new_description
        )

        result["regeneration_reason"] = reason
        result["character_id"] = character_id

        return result


class MockCharacterImageGenerator:
    """Mock character generator for testing."""

    async def generate_character_image(
        self,
        character_name: str,
        character_description: str,
        style: str = "anime"
    ) -> Dict:
        """Simulate character image generation."""
        logger.info(f"[MOCK] Generating character image for: {character_name}")

        return {
            "image_url": f"mock://character/{character_name.replace(' ', '_').lower()}.png",
            "prompt": f"Anime style character: {character_name} - {character_description}",
            "cost": Decimal("0.040"),
            "character_name": character_name
        }

    async def regenerate_character_image(
        self,
        character_id: str,
        character_name: str,
        new_description: str,
        reason: str = "appearance change"
    ) -> Dict:
        """Simulate character regeneration."""
        logger.info(f"[MOCK] Regenerating character: {character_name} (reason: {reason})")

        result = await self.generate_character_image(character_name, new_description)
        result["regeneration_reason"] = reason
        result["character_id"] = character_id

        return result
