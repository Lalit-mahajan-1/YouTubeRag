import uuid
from datetime import datetime

from pydantic import BaseModel


class NotesResponse(BaseModel):
    video_id: uuid.UUID
    title: str
    content: str  
    generated_at: datetime

    model_config = {"from_attributes": True}


class NotesGenerationResponse(BaseModel):
    message: str
    notes: NotesResponse