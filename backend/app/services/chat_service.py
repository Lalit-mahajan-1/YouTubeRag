import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.db.models.chat import Chat
from app.db.models.message import Message
from app.repositories.chat_repository import ChatRepository
from app.repositories.video_repository import VideoRepository

logger = get_logger(__name__)


class ChatServiceException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.video_repo = VideoRepository(db)

    async def create_chat(
        self,
        user_id: uuid.UUID,
        video_id: uuid.UUID,
        title: Optional[str] = None,
    ) -> Chat:
        # Verify video exists & belongs to user
        video = await self.video_repo.get_by_id(video_id, user_id)
        if not video:
            raise ChatServiceException("Video not found", 404)

        # Check if chat already exists for this video (one chat per video)
        existing = await self.chat_repo.get_by_video_id(video_id, user_id)
        if existing:
            return existing

        chat = await self.chat_repo.create_chat(
            user_id=user_id,
            video_id=video_id,
            title=title or video.title,
        )
        logger.info(f"Chat created: {chat.id} for video {video_id}")
        return chat

    async def get_chat(self, chat_id: uuid.UUID, user_id: uuid.UUID) -> Chat:
        chat = await self.chat_repo.get_by_id(chat_id, user_id)
        if not chat:
            raise ChatServiceException("Chat not found", 404)
        return chat

    async def get_messages(
        self, chat_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[Message]:
        # Verify chat ownership
        chat = await self.chat_repo.get_by_id(chat_id, user_id)
        if not chat:
            raise ChatServiceException("Chat not found", 404)

        return await self.chat_repo.get_messages(chat_id, user_id)

    async def get_user_chats(self, user_id: uuid.UUID) -> list[Chat]:
        return await self.chat_repo.get_user_chats(user_id)

    async def delete_chat(self, chat_id: uuid.UUID, user_id: uuid.UUID) -> None:
        deleted = await self.chat_repo.delete_chat(chat_id, user_id)
        if not deleted:
            raise ChatServiceException("Chat not found", 404)
        logger.info(f"Chat deleted: {chat_id}")