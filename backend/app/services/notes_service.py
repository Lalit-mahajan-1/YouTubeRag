import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.db.schemas.notes_schema import NotesResponse
from app.prompts.notes_prompt import note_prompt
from app.repositories.video_repository import VideoRepository
from app.services.llm_service import llm_service
from app.utils.pdf_generator import generate_pdf

logger = get_logger(__name__)


class NotesServiceException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotesService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.video_repo = VideoRepository(db)

    async def generate_notes(
        self, user_id: uuid.UUID, video_id: uuid.UUID
    ) -> NotesResponse:
        """Generate markdown notes from video transcript using LLM."""

        video = await self.video_repo.get_by_id(video_id, user_id)
        if not video:
            raise NotesServiceException("Video not found", 404)

        if not video.transcript:
            raise NotesServiceException("Video transcript not available", 400)

        try:
            prompt = note_prompt.format(context=video.transcript)
            content = await llm_service.generate(prompt)

            logger.info(f"Notes generated for video: {video_id}")

            return NotesResponse(
                video_id=video.id,
                title=video.title or f"Video {video.youtube_id}",
                content=content,
                generated_at=datetime.now(timezone.utc),
            )

        except Exception as e:
            logger.error(f"Failed to generate notes for {video_id}: {e}")
            raise NotesServiceException(
                f"Failed to generate notes: {str(e)}", 500
            )

    async def generate_notes_pdf(
        self, user_id: uuid.UUID, video_id: uuid.UUID
    ) -> tuple[bytes, str]:
        """Generate notes + convert to PDF. Returns (pdf_bytes, filename)."""

        notes = await self.generate_notes(user_id, video_id)

        try:
            pdf_bytes = generate_pdf(title=notes.title, content=notes.content)
            filename = f"notes_{notes.title[:50].replace(' ', '_')}.pdf"
            logger.info(f"PDF generated for video: {video_id}")
            return pdf_bytes, filename

        except Exception as e:
            logger.error(f"PDF generation failed for {video_id}: {e}")
            raise NotesServiceException(
                f"Failed to generate PDF: {str(e)}", 500
            )