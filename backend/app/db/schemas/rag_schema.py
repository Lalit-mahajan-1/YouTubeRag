import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ============ CHAT SCHEMAS ============

class CreateChatRequest(BaseModel):
    video_id: uuid.UUID
    title: Optional[str] = Field(None, max_length=255)


class ChatResponse(BaseModel):
    id: uuid.UUID
    video_id: uuid.UUID
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatListResponse(BaseModel):
    total: int
    chats: list[ChatResponse]


# ============ MESSAGE SCHEMAS ============

class MessageResponse(BaseModel):
    id: uuid.UUID
    chat_id: uuid.UUID
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    chat_id: uuid.UUID
    messages: list[MessageResponse]


# ============ RAG / ASK SCHEMAS ============

class AskQuestionRequest(BaseModel):
    chat_id: uuid.UUID
    question: str = Field(..., min_length=1, max_length=2000)


class SourceChunk(BaseModel):
    content: str
    score: Optional[float] = None


class AskQuestionResponse(BaseModel):
    answer: str
    chat_id: uuid.UUID
    message_id: uuid.UUID
    sources: Optional[list[SourceChunk]] = None