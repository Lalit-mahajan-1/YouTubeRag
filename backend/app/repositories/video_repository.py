import uuid
from typing import Optional, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.video import Video, VideoStatus
from app.core.constants import ErrorMessages


class VideoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: uuid.UUID,
        youtube_id: str,
        youtube_url: str,
        title: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        duration: Optional[int] = None,
        transcript: Optional[str] = None,
        pinecone_namespace: str = "",
    ) -> Video:
        video = Video(
            user_id=user_id,
            youtube_id=youtube_id,
            youtube_url=youtube_url,
            title=title,
            thumbnail_url=thumbnail_url,
            duration=duration,
            transcript=transcript,
            pinecone_namespace=pinecone_namespace,
            status=VideoStatus.PROCESSING,
        )
        self.db.add(video)
        await self.db.flush()
        await self.db.refresh(video)
        return video

    async def get_by_id(
        self, video_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Video]:
        """Get video only if it belongs to the user (security)"""
        result = await self.db.execute(
            select(Video).where(
                Video.id == video_id,
                Video.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_youtube_id_and_user(
        self, youtube_id: str, user_id: uuid.UUID
    ) -> Optional[Video]:
        """Prevent same user from processing same video twice"""
        result = await self.db.execute(
            select(Video).where(
                Video.youtube_id == youtube_id,
                Video.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(self, user_id: uuid.UUID) -> List[Video]:
        result = await self.db.execute(
            select(Video)
            .where(Video.user_id == user_id)
            .order_by(Video.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_status(
        self,
        video_id: uuid.UUID,
        status: str,
        error_message: Optional[str] = None,
        transcript: Optional[str] = None,
    ) -> Optional[Video]:
        stmt = (
            update(Video)
            .where(Video.id == video_id)
            .values(
                status=status,
                error_message=error_message,
                transcript=transcript,
            )
        )
        await self.db.execute(stmt)
        await self.db.commit()

        # Return updated video
        result = await self.db.execute(select(Video).where(Video.id == video_id))
        return result.scalar_one_or_none()

    async def delete(self, video_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        video = await self.get_by_id(video_id, user_id)
        if not video:
            return False

        await self.db.delete(video)
        await self.db.commit()
        return True