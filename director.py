"""Director AI - Claude Opus 4.5 for narrative planning."""

import logging
import json
from typing import Dict, List
from decimal import Decimal
from anthropic import Anthropic

from config import config

logger = logging.getLogger(__name__)


class Director:
    """Claude Opus 4.5 Director for episode planning."""

    def __init__(self):
        self.client = Anthropic(api_key=config.anthropic_api_key)
        self.model = config.director_model

    async def plan_episode(self, episode_number: int, context: Dict) -> Dict:
        """
        Generate a complete episode plan with 6 scenes.

        Args:
            episode_number: The episode number to generate
            context: Canon context (characters, recent events, world state)

        Returns:
            Dict with episode_summary, scenes list, and estimated_cost
        """
        logger.info(f"Director planning episode {episode_number}")

        # Build the prompt for Claude
        prompt = self._build_episode_prompt(episode_number, context)

        try:
            # Call Claude Opus 4.5
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=1.0,  # High creativity for narrative generation
                system=self._get_system_prompt(),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse the response
            content = response.content[0].text
            episode_plan = self._parse_episode_plan(content, episode_number)

            # Estimate cost (rough estimate based on token usage)
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)

            logger.info(f"Episode {episode_number} planned successfully (cost: ${cost:.4f})")
            logger.info(f"Summary: {episode_plan['episode_summary'][:100]}...")

            episode_plan["estimated_cost"] = cost
            return episode_plan

        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            raise

    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the Director's role."""
        return """You are the Director AI for an infinite anime series generator. Your role is to:

1. Plan cohesive, engaging anime episodes that continue an ongoing narrative
2. Create 6 consecutive 30-second scenes per episode that flow together seamlessly
3. Maintain character consistency and world-building across episodes
4. Generate vivid, detailed video prompts optimized for AI video generation
5. Balance action, dialogue, character development, and plot progression

CRITICAL RULES:
- Each episode must have EXACTLY 6 scenes
- Each scene is 30 seconds long
- Scene descriptions must be visual and cinematic (for video generation)
- Maintain continuity with previous episodes
- Create narrative hooks and cliffhangers to keep viewers engaged
- Characters should have consistent personalities and appearances
- World rules (physics, magic systems, etc.) must remain consistent

OUTPUT FORMAT:
You must respond with valid JSON in this exact structure:
{
  "episode_summary": "Brief 1-2 sentence summary of what happens in this episode",
  "scenes": [
    {
      "scene_in_episode": 1,
      "video_prompt": "Detailed visual description for AI video generation (anime style, camera angles, action, setting, lighting)",
      "narrative_summary": "What happens in this scene narratively"
    },
    ... (6 scenes total)
  ]
}

VIDEO PROMPT GUIDELINES:
- Start with "Anime style:" to set the visual tone
- Describe camera angles (close-up, wide shot, Dutch angle, etc.)
- Include lighting (dramatic shadows, bright daylight, neon glow, etc.)
- Specify action and movement clearly
- Describe character emotions and expressions
- Include environmental details
- Keep it under 400 characters for optimal video generation

NARRATIVE QUALITY:
- Create emotional resonance and character depth
- Use anime storytelling conventions (dramatic reveals, power-ups, internal monologues)
- Build tension and release it strategically
- Mix high-action scenes with quieter character moments
- End episodes with compelling hooks for the next episode"""

    def _build_episode_prompt(self, episode_number: int, context: Dict) -> str:
        """Build the user prompt with context."""
        # Extract context information
        recent_events = context.get("recent_events", [])
        characters = context.get("characters", {})
        current_arc = context.get("current_arc", "Beginning")
        open_threads = context.get("open_threads", [])

        # Format recent events
        events_text = "\n".join([f"- {event}" for event in recent_events[-10:]])  # Last 10 events
        if not events_text:
            events_text = "- This is the very first episode! Establish the world, introduce main characters, and set up the initial conflict."

        # Format characters
        if characters:
            chars_text = "\n".join([
                f"- {char_id}: {info.get('name', 'Unknown')} - {info.get('canonical_state', 'No description')}"
                for char_id, info in characters.items()
            ])
        else:
            chars_text = "- No characters established yet. Create compelling main characters for this new anime series."

        # Format open threads
        threads_text = "\n".join([f"- {thread}" for thread in open_threads])
        if not threads_text:
            threads_text = "- No open plot threads yet"

        prompt = f"""Plan Episode {episode_number} of the infinite anime series.

CURRENT NARRATIVE CONTEXT:
Current Arc: {current_arc}

Recent Events:
{events_text}

Established Characters:
{chars_text}

Open Plot Threads:
{threads_text}

TASK:
Create an engaging episode with 6 scenes (30 seconds each) that:
1. Continues the narrative naturally from where we left off
2. {"Introduces the world and main characters" if episode_number == 1 else "Develops existing characters and plot threads"}
3. Includes a mix of action, emotion, and story progression
4. Ends with a compelling hook for the next episode

Remember: Output must be valid JSON following the exact format specified in your system instructions."""

        return prompt

    def _parse_episode_plan(self, content: str, episode_number: int) -> Dict:
        """Parse Claude's response into structured episode plan."""
        try:
            # Try to extract JSON from the response
            # Claude might wrap it in markdown code blocks
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()

            plan = json.loads(content)

            # Validate structure
            if "episode_summary" not in plan or "scenes" not in plan:
                raise ValueError("Missing required fields in episode plan")

            if len(plan["scenes"]) != 6:
                raise ValueError(f"Expected 6 scenes, got {len(plan['scenes'])}")

            # Ensure scene_in_episode is set correctly
            for i, scene in enumerate(plan["scenes"], 1):
                if "scene_in_episode" not in scene:
                    scene["scene_in_episode"] = i
                if "video_prompt" not in scene or "narrative_summary" not in scene:
                    raise ValueError(f"Scene {i} missing required fields")

            plan["episode_number"] = episode_number
            return plan

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Claude response: {e}")
            logger.error(f"Content: {content[:500]}...")
            raise ValueError(f"Director returned invalid JSON: {e}")
        except Exception as e:
            logger.error(f"Error parsing episode plan: {e}")
            raise

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        """
        Calculate cost for Claude Opus 4.5 API call.

        Pricing (as of 2025):
        - Input: $15 per million tokens
        - Output: $75 per million tokens
        """
        input_cost = Decimal(input_tokens) * Decimal("15.00") / Decimal("1000000")
        output_cost = Decimal(output_tokens) * Decimal("75.00") / Decimal("1000000")
        total = input_cost + output_cost
        return total.quantize(Decimal("0.0001"))
