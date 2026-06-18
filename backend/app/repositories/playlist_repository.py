import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.playlist import Playlist, PlaylistStatus


class PlaylistRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: uuid.UUID,
        youtube_playlist_id: str,
        youtube_url: str,
        title: Optional[str] = None,
        total_videos: int = 0,
    ) -> Playlist:
        playlist = Playlist(
            user_id=user_id,
            youtube_playlist_id=youtube_playlist_id,
            youtube_url=youtube_url,
            title=title,
            total_videos=total_videos,
            video_summaries=[],
            status=PlaylistStatus.PROCESSING,
        )
        self.db.add(playlist)
        await self.db.flush()
        await self.db.refresh(playlist)
        return playlist

    async def get_by_id(
        self, playlist_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Playlist]:
        result = await self.db.execute(
            select(Playlist).where(
                Playlist.id == playlist_id,
                Playlist.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_youtube_id(
        self, youtube_playlist_id: str, user_id: uuid.UUID
    ) -> Optional[Playlist]:
        result = await self.db.execute(
            select(Playlist).where(
                Playlist.youtube_playlist_id == youtube_playlist_id,
                Playlist.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(self, user_id: uuid.UUID) -> list[Playlist]:
        result = await self.db.execute(
            select(Playlist)
            .where(Playlist.user_id == user_id)
            .order_by(Playlist.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_summaries_and_status(
        self,
        playlist_id: uuid.UUID,
        video_summaries: list[dict],
        status: str,
        error_message: Optional[str] = None,
    ) -> Optional[Playlist]:
        playlist = await self.db.get(Playlist, playlist_id)
        if not playlist:
            return None

        playlist.video_summaries = video_summaries
        playlist.status = status
        playlist.error_message = error_message
        await self.db.flush()
        await self.db.refresh(playlist)
        return playlist

    async def delete(self, playlist_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        playlist = await self.get_by_id(playlist_id, user_id)
        if not playlist:
            return False
        await self.db.delete(playlist)
        await self.db.commit()
        return True