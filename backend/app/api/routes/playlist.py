import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, get_playlist_service
from app.db.models.user import User
from app.db.schemas.playlist_schema import (
    PlaylistListResponse,
    PlaylistResponse,
    ProcessPlaylistRequest,
    ProcessPlaylistResponse,
)
from app.services.playlist_service import PlaylistService, PlaylistServiceException

router = APIRouter(prefix="/playlist", tags=["Playlist"])


@router.post(
    "/process",
    response_model=ProcessPlaylistResponse,
    status_code=status.HTTP_201_CREATED,
)
async def process_playlist(
    payload: ProcessPlaylistRequest,
    user: User = Depends(get_current_user),
    service: PlaylistService = Depends(get_playlist_service),
):
    try:
        playlist = await service.process_playlist(user.id, payload)
        return ProcessPlaylistResponse(
            message="Playlist processed successfully",
            playlist=PlaylistResponse.model_validate(playlist),
        )
    except PlaylistServiceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/list", response_model=PlaylistListResponse)
async def list_playlists(
    user: User = Depends(get_current_user),
    service: PlaylistService = Depends(get_playlist_service),
):
    playlists = await service.get_user_playlists(user.id)
    return PlaylistListResponse(
        total=len(playlists),
        playlists=[PlaylistResponse.model_validate(p) for p in playlists],
    )


@router.get("/{playlist_id}", response_model=PlaylistResponse)
async def get_playlist(
    playlist_id: uuid.UUID,
    user: User = Depends(get_current_user),
    service: PlaylistService = Depends(get_playlist_service),
):
    try:
        playlist = await service.get_playlist(playlist_id, user.id)
        return PlaylistResponse.model_validate(playlist)
    except PlaylistServiceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playlist(
    playlist_id: uuid.UUID,
    user: User = Depends(get_current_user),
    service: PlaylistService = Depends(get_playlist_service),
):
    try:
        await service.delete_playlist(playlist_id, user.id)
    except PlaylistServiceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)