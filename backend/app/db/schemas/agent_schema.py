import uuid
from typing import Optional

from pydantic import BaseModel, Field


class AgentAskRequest(BaseModel):
    playlist_id: uuid.UUID
    question: str = Field(..., min_length=1, max_length=2000)


class AgentSource(BaseModel):
    video_id: str
    video_title: str


class AgentAskResponse(BaseModel):
    answer: str
    selected_videos: list[AgentSource]
    total_chunks_used: int