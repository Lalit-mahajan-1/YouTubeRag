import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.chat import Chat


class VideoStatus:
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Video(Base):
    __tablename__ = "videos"
    __table_args__ = (
        UniqueConstraint("user_id", "youtube_id", name="uq_user_video"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    youtube_id: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    youtube_url: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)  # seconds

    transcript: Mapped[str] = mapped_column(Text, nullable=True)
    pinecone_namespace: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    status: Mapped[str] = mapped_column(
        String(20), default=VideoStatus.PROCESSING, nullable=False, index=True
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

    # Relationships
    user: Mapped["User"] = relationship(back_populates="videos")
    chats: Mapped[list["Chat"]] = relationship(
        back_populates="video", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Video {self.youtube_id} ({self.status})>"