from langchain_core.documents import Document

from app.core.config import settings
from app.core.logger import get_logger
from app.services.embedding_service import embedding_service

logger = get_logger(__name__)


class RetrievalService:
    def __init__(self):
        self.top_k = settings.RETRIEVAL_TOP_K

    async def retrieve(self, question: str, namespace: str) -> list[Document]:
        """Retrieve top-K relevant chunks from Pinecone for a question."""
        vector_store = embedding_service.get_vector_store(namespace)

        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.top_k},
        )

        docs = retriever.invoke(question)
        logger.info(f"Retrieved {len(docs)} chunks for namespace: {namespace}")
        return docs

    @staticmethod
    def format_context(docs: list[Document]) -> str:
        """Combine retrieved chunks into a single context string."""
        return "\n\n".join(doc.page_content for doc in docs)