import re
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


PLAYLIST_URL_PATTERN = re.compile(
    r"^(https?://)?(www\.)?youtube\.com/(playlist\?list=|watch\?.*list=)[\w-]+.*$"
)


class ProcessPlaylistRequest(BaseModel):
    youtube_url: str = Field(..., min_length=10, max_length=500)

    @field_validator("youtube_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not PLAYLIST_URL_PATTERN.match(v):
            raise ValueError("Invalid YouTube playlist URL")
        return v


class VideoSummary(BaseModel):
    video_id: uuid.UUID
    youtube_id: str
    title: str
    keywords: list[str]


class PlaylistResponse(BaseModel):
    id: uuid.UUID
    youtube_playlist_id: str
    youtube_url: str
    title: Optional[str] = None
    total_videos: int
    video_summaries: list[VideoSummary]
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProcessPlaylistResponse(BaseModel):
    message: str
    playlist: PlaylistResponse


class PlaylistListResponse(BaseModel):
    total: int
    playlists: list[PlaylistResponse]