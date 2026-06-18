from keybert import KeyBERT

from app.core.logger import get_logger

logger = get_logger(__name__)


class KeywordService:
    """Singleton — loads KeyBERT model once at startup."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        logger.info("Initializing KeyBERT model...")
        # Uses sentence-transformers under the hood (same model you already have)
        self.model = KeyBERT(model="sentence-transformers/all-MiniLM-L6-v2")
        self._initialized = True
        logger.info("KeyBERT ready")

    def extract_keywords(
        self, text: str, top_n: int = 8
    ) -> list[str]:
        """
        Extract top N keywords/keyphrases from text.

        Returns list of keywords (e.g., ["jwt auth", "tokens", "security"])
        """
        if not text or not text.strip():
            return []

        try:
            # Extract keyphrases of 1-2 words, avoiding duplicates
            keywords = self.model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 2),
                stop_words="english",
                top_n=top_n,
                use_mmr=True,  # Maximal Marginal Relevance for diversity
                diversity=0.5,
            )

            # Returns list of tuples [(keyword, score), ...]
            return [kw for kw, _ in keywords]

        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []


# Global singleton
keyword_service = KeywordService()