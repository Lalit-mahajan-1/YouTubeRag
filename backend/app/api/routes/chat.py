import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_chat_service, get_current_user
from app.db.models.user import User
from app.db.schemas.rag_schema import (
    ChatHistoryResponse,
    ChatListResponse,
    ChatResponse,
    CreateChatRequest,
    MessageResponse,
)
from app.services.chat_service import ChatService, ChatServiceException

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/create", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    payload: CreateChatRequest,
    user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    try:
        chat = await service.create_chat(user.id, payload.video_id, payload.title)
        return ChatResponse.model_validate(chat)
    except ChatServiceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/list", response_model=ChatListResponse)
async def list_chats(
    user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    chats = await service.get_user_chats(user.id)
    return ChatListResponse(
        total=len(chats),
        chats=[ChatResponse.model_validate(c) for c in chats],
    )


@router.get("/{chat_id}/messages", response_model=ChatHistoryResponse)
async def get_messages(
    chat_id: uuid.UUID,
    user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    try:
        messages = await service.get_messages(chat_id, user.id)
        return ChatHistoryResponse(
            chat_id=chat_id,
            messages=[MessageResponse.model_validate(m) for m in messages],
        )
    except ChatServiceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: uuid.UUID,
    user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    try:
        await service.delete_chat(chat_id, user.id)
    except ChatServiceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)