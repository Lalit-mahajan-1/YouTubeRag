import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.video import Video


class PlaylistStatus:
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    youtube_playlist_id: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    youtube_url: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    total_videos: Mapped[int] = mapped_column(Integer, default=0)

    # JSON cache: [{video_id, youtube_id, title, keywords}]
    video_summaries: Mapped[list] = mapped_column(JSONB, default=list)

    status: Mapped[str] = mapped_column(
        String(20), default=PlaylistStatus.PROCESSING, nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="playlists")
    videos: Mapped[list["Video"]] = relationship(
        back_populates="playlist", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Playlist {self.youtube_playlist_id} ({self.status})>"