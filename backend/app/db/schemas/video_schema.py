import re
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


YOUTUBE_URL_PATTERN = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com/(watch\?v=|embed/)|youtu\.be/)[\w-]{11}.*$"
)


class ProcessVideoRequest(BaseModel):
    youtube_url: str = Field(..., min_length=10, max_length=500)

    @field_validator("youtube_url")
    @classmethod
    def validate_youtube_url(cls, v: str) -> str:
        if not YOUTUBE_URL_PATTERN.match(v):
            raise ValueError("Invalid YouTube URL")
        return v


class VideoResponse(BaseModel):
    id: uuid.UUID
    youtube_id: str
    youtube_url: str
    title: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VideoListResponse(BaseModel):
    total: int
    videos: list[VideoResponse]


class ProcessVideoResponse(BaseModel):
    message: str
    video: VideoResponse   


class VideoStatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}