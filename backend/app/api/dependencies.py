from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.user import User
from app.services.auth_service import AuthException, AuthService
from app.services.chat_service import ChatService
from app.services.rag_service import RAGService
from app.services.youtube_service import YouTubeService
from app.services.notes_service import NotesService
from app.services.playlist_service import PlaylistService


bearer_scheme = HTTPBearer()
async def get_playlist_service(db: AsyncSession = Depends(get_db)) -> PlaylistService:
    return PlaylistService(db)

async def get_notes_service(db: AsyncSession = Depends(get_db)) -> NotesService:
    return NotesService(db)
    
async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


async def get_youtube_service(db: AsyncSession = Depends(get_db)) -> YouTubeService:
    return YouTubeService(db)


async def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    return ChatService(db)


async def get_rag_service(db: AsyncSession = Depends(get_db)) -> RAGService:
    return RAGService(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    try:
        return await auth_service.get_current_user(credentials.credentials)
    except AuthException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)