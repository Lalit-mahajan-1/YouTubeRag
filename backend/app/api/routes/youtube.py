import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, get_youtube_service
from app.db.models.user import User
from app.db.schemas.video_schema import (
    ProcessVideoRequest,
    ProcessVideoResponse,
    VideoListResponse,
    VideoResponse,
)
from app.services.youtube_service import YouTubeService, YouTubeServiceException

router = APIRouter(prefix="/youtube", tags=["YouTube"])


@router.post("/process", response_model=ProcessVideoResponse, status_code=status.HTTP_201_CREATED)
async def process_video(
    payload: ProcessVideoRequest,
    user: User = Depends(get_current_user),
    service: YouTubeService = Depends(get_youtube_service),
):
    try:
        video = await service.process_video(user.id, payload)
        return ProcessVideoResponse(
            message="Video processed successfully",
            video=VideoResponse.model_validate(video),
        )
    except YouTubeServiceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/videos", response_model=VideoListResponse)
async def list_videos(
    user: User = Depends(get_current_user),
    service: YouTubeService = Depends(get_youtube_service),
):
    videos = await service.get_user_videos(user.id)
    return VideoListResponse(
        total=len(videos),
        videos=[VideoResponse.model_validate(v) for v in videos],
    )


@router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: uuid.UUID,
    user: User = Depends(get_current_user),
    service: YouTubeService = Depends(get_youtube_service),
):
    try:
        video = await service.get_video(video_id, user.id)
        return VideoResponse.model_validate(video)
    except YouTubeServiceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: uuid.UUID,
    user: User = Depends(get_current_user),
    service: YouTubeService = Depends(get_youtube_service),
):
    try:
        await service.delete_video(video_id, user.id)
    except YouTubeServiceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)