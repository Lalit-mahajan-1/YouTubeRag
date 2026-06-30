import json
import math

from app.agents.state import AgentState
from app.core.logger import get_logger
from app.prompts.router_prompt import ROUTER_PROMPT
from app.services.llm_service import llm_service

logger = get_logger(__name__)


async def router_node(state: AgentState) -> dict:
    """Decides which videos are relevant to the question."""

    video_summaries = state["video_summaries"]
    question = state["question"]

    if not video_summaries:
        logger.warning("No video summaries available")
        return {"selected_video_ids": []}

    # Max 30% of total videos (at least 1)
    max_videos = max(1, math.ceil(len(video_summaries) * 0.3))

    # Build readable video list for LLM
    videos_text = "\n".join(
        [
            f'- ID: "{v["video_id"]}" | Title: "{v["title"]}" | Keywords: {", ".join(v.get("keywords", []))}'
            for v in video_summaries
        ]
    )

    prompt = ROUTER_PROMPT.format(
        max_videos=max_videos,
        question=question,
        videos=videos_text,
    )

    try:
        response = await llm_service.generate(prompt)
        response = response.strip()

        # Clean markdown code blocks if present
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
        response = response.strip()

        selected = json.loads(response)
        if not isinstance(selected, list):
            selected = []

        # Validate IDs exist in playlist
        valid_ids = {v["video_id"] for v in video_summaries}
        selected = [vid for vid in selected if vid in valid_ids][:max_videos]

        logger.info(
            f"Router selected {len(selected)}/{len(video_summaries)} videos"
        )
        return {"selected_video_ids": selected}

    except Exception as e:
        logger.error(f"Router failed: {e}")
        # Fallback: take first N videos
        fallback = [v["video_id"] for v in video_summaries[:max_videos]]
        return {"selected_video_ids": fallback}