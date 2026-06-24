from langchain_pinecone import PineconeEmbeddings, PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        logger.info("Initializing Pinecone hosted embeddings...")

        self.embedding_model = PineconeEmbeddings(
            model="multilingual-e5-large",
            pinecone_api_key=settings.PINECONE_API_KEY,
        )

        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)

        existing = [idx.name for idx in self.pc.list_indexes()]
        if settings.PINECONE_INDEX_NAME not in existing:
            logger.info(f"Creating index: {settings.PINECONE_INDEX_NAME}")
            self.pc.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=1024,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

        self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
        self._initialized = True
        logger.info("Embedding service ready")

    def get_vector_store(self, namespace: str) -> PineconeVectorStore:
        return PineconeVectorStore(
            index=self.index,
            embedding=self.embedding_model,
            namespace=namespace,
            text_key="text",
        )

    async def store_chunks(self, chunks, namespace: str) -> None:
        if not chunks:
            raise ValueError("No chunks to store")
        vector_store = self.get_vector_store(namespace)
        vector_store.add_documents(chunks)
        logger.info(f"Stored {len(chunks)} chunks in namespace: {namespace}")

    def delete_namespace(self, namespace: str) -> None:
        try:
            self.index.delete(delete_all=True, namespace=namespace)
            logger.info(f"Deleted namespace: {namespace}")
        except Exception as e:
            logger.error(f"Failed to delete namespace {namespace}: {e}")


embedding_service = EmbeddingService()