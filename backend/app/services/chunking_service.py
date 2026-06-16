from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class ChunkingService:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

    def chunk_text(self, text: str) -> list[Document]:
        """Splits transcript text into overlapping chunks."""
        if not text or not text.strip():
            raise ValueError("Cannot chunk empty text")

        chunks = self.splitter.create_documents([text])
        logger.info(f"Created {len(chunks)} chunks from transcript")
        return chunks