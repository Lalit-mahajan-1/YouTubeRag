import uuid
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.chat import Chat
from app.db.models.message import Message, MessageRole


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat(
        self,
        user_id: uuid.UUID,
        video_id: uuid.UUID,
        title: Optional[str] = None,
    ) -> Chat:
        chat = Chat(
            user_id=user_id,
            video_id=video_id,
            title=title,
        )
        self.db.add(chat)
        await self.db.flush()
        await self.db.refresh(chat)
        return chat

    async def get_by_id(
        self, chat_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Chat]:
        """Get chat only if it belongs to the user"""
        result = await self.db.execute(
            select(Chat)
            .where(Chat.id == chat_id, Chat.user_id == user_id)
            .options(selectinload(Chat.messages))
        )
        return result.scalar_one_or_none()

    async def get_by_video_id(
        self, video_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Chat]:
        """Get chat associated with a specific video"""
        result = await self.db.execute(
            select(Chat)
            .where(Chat.video_id == video_id, Chat.user_id == user_id)
            .options(selectinload(Chat.messages))
        )
        return result.scalar_one_or_none()

    async def get_user_chats(self, user_id: uuid.UUID) -> List[Chat]:
        result = await self.db.execute(
            select(Chat)
            .where(Chat.user_id == user_id)
            .options(selectinload(Chat.video))
            .order_by(Chat.updated_at.desc())
        )
        return list(result.scalars().all())

    async def add_message(
        self, chat_id: uuid.UUID, role: str, content: str
    ) -> Message:
        message = Message(
            chat_id=chat_id,
            role=role,
            content=content,
        )
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def get_messages(
        self, chat_id: uuid.UUID, user_id: uuid.UUID
    ) -> List[Message]:
        result = await self.db.execute(
            select(Message)
            .join(Chat)
            .where(Message.chat_id == chat_id, Chat.user_id == user_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())

    async def delete_chat(self, chat_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        chat = await self.get_by_id(chat_id, user_id)
        if not chat:
            return False

        await self.db.delete(chat)
        await self.db.commit()
        return True