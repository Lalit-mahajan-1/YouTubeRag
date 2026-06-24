import json

from app.core.logger import get_logger
from app.services.llm_service import llm_service

logger = get_logger(__name__)


class KeywordService:
    @staticmethod
    async def extract_keywords(text: str, top_n: int = 8) -> list[str]:
        """Extract keywords using Groq LLM."""
        if not text or not text.strip():
            return []

        snippet = text[:2000]

        prompt = f"""Extract exactly {top_n} keywords or short keyphrases (1-3 words each) from this text.
Return ONLY a JSON array of strings, nothing else.

Text:
{snippet}

Output (JSON array only):"""

        try:
            response = await llm_service.generate(prompt)
            response = response.strip()

            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()

            keywords = json.loads(response)
            return keywords[:top_n] if isinstance(keywords, list) else []

        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []


keyword_service = KeywordService()