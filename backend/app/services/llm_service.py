from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    """Singleton wrapper around the LLM."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        logger.info(f"Initializing LLM: {settings.LLM_MODEL}")
        self.llm = ChatGroq(
            model=settings.LLM_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0.2,
        )
        self.parser = StrOutputParser()
        self._initialized = True

    async def generate(self, prompt: str) -> str:
        """Send prompt to LLM and return parsed string response."""
        try:
            chain = self.llm | self.parser
            response = await chain.ainvoke(prompt)
            return response
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise


# Global singleton
llm_service = LLMService()