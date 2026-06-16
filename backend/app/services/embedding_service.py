from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Singleton — initialize ONCE at app startup."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        logger.info("Initializing embedding model and Pinecone...")

        # Load HuggingFace embedding model (takes 5-10s)
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )

        # Initialize Pinecone
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)

        # Create index if not exists
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        if settings.PINECONE_INDEX_NAME not in existing_indexes:
            logger.info(f"Creating Pinecone index: {settings.PINECONE_INDEX_NAME}")
            self.pc.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=384,  # all-MiniLM-L6-v2 dimension
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

        self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
        self._initialized = True
        logger.info("Embedding service ready")

    def get_vector_store(self, namespace: str) -> PineconeVectorStore:
        """Get a vector store scoped to a specific namespace."""
        return PineconeVectorStore(
            index=self.index,
            embedding=self.embedding_model,
            namespace=namespace,
            text_key="text",
        )

    async def store_chunks(self, chunks: list[Document], namespace: str) -> None:
        """Embed chunks and store them in Pinecone under a namespace."""
        if not chunks:
            raise ValueError("No chunks to store")

        vector_store = self.get_vector_store(namespace)
        vector_store.add_documents(chunks)
        logger.info(f"Stored {len(chunks)} chunks in namespace: {namespace}")

    def delete_namespace(self, namespace: str) -> None:
        """Delete all vectors for a video (when user deletes video)."""
        try:
            self.index.delete(delete_all=True, namespace=namespace)
            logger.info(f"Deleted namespace: {namespace}")
        except Exception as e:
            logger.error(f"Failed to delete namespace {namespace}: {e}")


# Global singleton
embedding_service = EmbeddingService()