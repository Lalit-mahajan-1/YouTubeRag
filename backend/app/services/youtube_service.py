import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.db.models.video import Video, VideoStatus
from app.db.schemas.video_schema import ProcessVideoRequest
from app.repositories.video_repository import VideoRepository
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import embedding_service
from app.services.transcript_service import TranscriptException, TranscriptService
from app.utils.youtube_parser import extract_video_id

logger = get_logger(__name__)


class YouTubeServiceException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class YouTubeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.video_repo = VideoRepository(db)
        self.chunking_service = ChunkingService()

    async def process_video(
        self, user_id: uuid.UUID, data: ProcessVideoRequest
    ) -> Video:
        """Full pipeline: fetch transcript → chunk → embed → store."""

        # 1. Extract video ID
        try:
            youtube_id = extract_video_id(data.youtube_url)
        except ValueError as e:
            raise YouTubeServiceException(str(e), 400)

        # 2. Check if already processed by this user
        existing = await self.video_repo.get_by_youtube_id_and_user(
            youtube_id, user_id
        )
        if existing and existing.status == VideoStatus.READY:
            logger.info(f"Video already processed: {youtube_id}")
            return existing

        # 3. Fetch transcript
        try:
            _, transcript = await TranscriptService.get_transcript(data.youtube_url)
        except TranscriptException as e:
            raise YouTubeServiceException(e.message, e.status_code)

        # 4. Create video record (status=processing)
        namespace = f"user_{user_id}_video_{youtube_id}"
        video = await self.video_repo.create(
            user_id=user_id,
            youtube_id=youtube_id,
            youtube_url=data.youtube_url,
            title=f"Video {youtube_id}",  # Update with actual title later
            transcript=transcript,
            pinecone_namespace=namespace,
        )

        # 5. Chunk + embed + store
        try:
            chunks = self.chunking_service.chunk_text(transcript)
            await embedding_service.store_chunks(chunks, namespace=namespace)

            # 6. Mark as ready
            await self.video_repo.update_status(
                video.id, VideoStatus.READY, transcript=transcript
            )
            logger.info(f"Video processed successfully: {video.id}")

        except Exception as e:
            logger.error(f"Processing failed for {video.id}: {e}")
            await self.video_repo.update_status(
                video.id, VideoStatus.FAILED, error_message=str(e)
            )
            raise YouTubeServiceException(f"Processing failed: {str(e)}", 500)

        # Refresh and return
        return await self.video_repo.get_by_id(video.id, user_id)

    async def get_user_videos(self, user_id: uuid.UUID) -> list[Video]:
        return await self.video_repo.get_all_by_user(user_id)

    async def get_video(self, video_id: uuid.UUID, user_id: uuid.UUID) -> Video:
        video = await self.video_repo.get_by_id(video_id, user_id)
        if not video:
            raise YouTubeServiceException("Video not found", 404)
        return video

    async def delete_video(self, video_id: uuid.UUID, user_id: uuid.UUID) -> None:
        video = await self.video_repo.get_by_id(video_id, user_id)
        if not video:
            raise YouTubeServiceException("Video not found", 404)

        # Delete from Pinecone first
        embedding_service.delete_namespace(video.pinecone_namespace)

        # Then delete from DB
        await self.video_repo.delete(video_id, user_id)
        logger.info(f"Video deleted: {video_id}")