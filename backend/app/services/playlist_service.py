import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.db.models.playlist import Playlist, PlaylistStatus
from app.db.models.video import VideoStatus
from app.db.schemas.playlist_schema import ProcessPlaylistRequest
from app.db.schemas.video_schema import ProcessVideoRequest
from app.repositories.playlist_repository import PlaylistRepository
from app.repositories.video_repository import VideoRepository
from app.services.keyword_service import keyword_service
from app.services.youtube_service import YouTubeService, YouTubeServiceException
from app.utils.playlist_parser import extract_playlist_id, fetch_playlist_videos

logger = get_logger(__name__)


class PlaylistServiceException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class PlaylistService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.playlist_repo = PlaylistRepository(db)
        self.video_repo = VideoRepository(db)
        self.youtube_service = YouTubeService(db)

    async def process_playlist(
        self, user_id: uuid.UUID, data: ProcessPlaylistRequest
    ) -> Playlist:
        """Full pipeline: extract videos → process each → extract keywords."""

        # 1. Extract playlist ID
        try:
            playlist_yt_id = extract_playlist_id(data.youtube_url)
        except ValueError as e:
            raise PlaylistServiceException(str(e), 400)

        # 2. Check if already exists
        existing = await self.playlist_repo.get_by_youtube_id(
            playlist_yt_id, user_id
        )
        if existing and existing.status == PlaylistStatus.READY:
            logger.info(f"Playlist already processed: {playlist_yt_id}")
            return existing

        # 3. Fetch playlist videos metadata
        try:
            playlist_title, videos_meta = fetch_playlist_videos(data.youtube_url)
        except ValueError as e:
            raise PlaylistServiceException(str(e), 400)

        if not videos_meta:
            raise PlaylistServiceException("Playlist is empty", 400)

        # 4. Create playlist record (status=processing)
        playlist = await self.playlist_repo.create(
            user_id=user_id,
            youtube_playlist_id=playlist_yt_id,
            youtube_url=data.youtube_url,
            title=playlist_title,
            total_videos=len(videos_meta),
        )
        await self.db.commit()

        # 5. Process each video sequentially (to avoid rate-limiting)
        video_summaries = []
        for vid in videos_meta:
            summary = await self._process_single_video(
                user_id=user_id,
                playlist_id=playlist.id,
                video_url=vid["url"],
                video_title=vid["title"],
            )
            if summary:
                video_summaries.append(summary)

        # 6. Update playlist with summaries + mark ready
        final_status = (
            PlaylistStatus.READY if video_summaries else PlaylistStatus.FAILED
        )
        await self.playlist_repo.update_summaries_and_status(
            playlist_id=playlist.id,
            video_summaries=video_summaries,
            status=final_status,
        )
        await self.db.commit()

        logger.info(
            f"Playlist {playlist.id} processed: "
            f"{len(video_summaries)}/{len(videos_meta)} videos ready"
        )

        return await self.playlist_repo.get_by_id(playlist.id, user_id)

    async def _process_single_video(
        self,
        user_id: uuid.UUID,
        playlist_id: uuid.UUID,
        video_url: str,
        video_title: str,
    ) -> dict | None:
        """Process one video and return its summary dict (or None if failed)."""
        try:
            # Reuse existing YouTubeService
            video = await self.youtube_service.process_video(
                user_id=user_id,
                data=ProcessVideoRequest(youtube_url=video_url),
            )

            # Link to playlist
            video.playlist_id = playlist_id
            await self.db.flush()

            # Extract keywords from transcript
            keywords = []
            if video.transcript:
                keywords = await keyword_service.extract_keywords(video.transcript, top_n=8)

            await self.db.commit()

            return {
                "video_id": str(video.id),
                "youtube_id": video.youtube_id,
                "title": video.title or video_title,
                "keywords": keywords,
            }

        except YouTubeServiceException as e:
            logger.warning(f"Skipping video {video_url}: {e.message}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {video_url}: {e}")
            return None

    async def get_user_playlists(self, user_id: uuid.UUID) -> list[Playlist]:
        return await self.playlist_repo.get_all_by_user(user_id)

    async def get_playlist(
        self, playlist_id: uuid.UUID, user_id: uuid.UUID
    ) -> Playlist:
        playlist = await self.playlist_repo.get_by_id(playlist_id, user_id)
        if not playlist:
            raise PlaylistServiceException("Playlist not found", 404)
        return playlist

    async def delete_playlist(
        self, playlist_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        deleted = await self.playlist_repo.delete(playlist_id, user_id)
        if not deleted:
            raise PlaylistServiceException("Playlist not found", 404)
        logger.info(f"Playlist deleted: {playlist_id}")