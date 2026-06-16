import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.db.models.message import MessageRole
from app.db.models.video import VideoStatus
from app.prompts.rag_prompt import rag_prompt
from app.repositories.chat_repository import ChatRepository
from app.repositories.video_repository import VideoRepository
from app.services.llm_service import llm_service
from app.services.retrieval_service import RetrievalService

logger = get_logger(__name__)


class RAGServiceException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class RAGService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.video_repo = VideoRepository(db)
        self.retrieval_service = RetrievalService()

    async def ask_question(
        self,
        user_id: uuid.UUID,
        chat_id: uuid.UUID,
        question: str,
    ) -> dict:
        # 1. Verify chat exists & belongs to user
        chat = await self.chat_repo.get_by_id(chat_id, user_id)
        if not chat:
            raise RAGServiceException("Chat not found", 404)

        # 2. Get associated video
        video = await self.video_repo.get_by_id(chat.video_id, user_id)
        if not video:
            raise RAGServiceException("Video not found", 404)

        if video.status != VideoStatus.READY:
            raise RAGServiceException(
                f"Video is not ready (status: {video.status})", 400
            )

        # 3. Save user message
        user_msg = await self.chat_repo.add_message(
            chat_id=chat_id,
            role=MessageRole.USER,
            content=question,
        )

        try:
            # 4. Retrieve relevant chunks
            docs = await self.retrieval_service.retrieve(
                question=question,
                namespace=video.pinecone_namespace,
            )
            context = self.retrieval_service.format_context(docs)

            # 5. Build prompt
            formatted_prompt = rag_prompt.format(
                context=context,
                question=question,
            )

            # 6. Generate answer
            answer = await llm_service.generate(formatted_prompt)

            # 7. Save assistant message
            assistant_msg = await self.chat_repo.add_message(
                chat_id=chat_id,
                role=MessageRole.ASSISTANT,
                content=answer,
            )

            logger.info(f"RAG answer generated for chat {chat_id}")

            return {
                "answer": answer,
                "chat_id": chat_id,
                "message_id": assistant_msg.id,
                "sources": [
                    {"content": doc.page_content, "score": None} for doc in docs
                ],
            }

        except Exception as e:
            logger.error(f"RAG failed for chat {chat_id}: {e}")
            # Save error as assistant message
            await self.chat_repo.add_message(
                chat_id=chat_id,
                role=MessageRole.ASSISTANT,
                content="Sorry, I couldn't generate an answer. Please try again.",
            )
            raise RAGServiceException(f"Failed to generate answer: {str(e)}", 500)