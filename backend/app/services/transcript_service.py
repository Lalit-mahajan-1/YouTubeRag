from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

from app.core.logger import get_logger
from app.utils.youtube_parser import extract_video_id
from app.utils.transcript_cleaner import clean_transcript

logger = get_logger(__name__)


class TranscriptException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class TranscriptService:
    @staticmethod
    async def get_transcript(youtube_url: str) -> tuple[str, str]:
        try:
            video_id = extract_video_id(youtube_url)
        except ValueError as e:
            raise TranscriptException(str(e), 400)

        try:
            api = YouTubeTranscriptApi()
            fetched = api.fetch(video_id)
            transcript_list = [{"text": s.text} for s in fetched]

            full_text = " ".join([item["text"] for item in transcript_list])
            cleaned_text = clean_transcript(full_text)

            if not cleaned_text.strip():
                raise TranscriptException("Transcript is empty", 422)

            logger.info(f"Transcript fetched: {video_id} ({len(cleaned_text)} chars)")
            return video_id, cleaned_text

        except TranscriptsDisabled:
            raise TranscriptException("Transcripts are disabled for this video", 422)
        except NoTranscriptFound:
            raise TranscriptException("No transcript available for this video", 404)
        except VideoUnavailable:
            raise TranscriptException("Video is unavailable or private", 404)
        except Exception as e:
            logger.error(f"Failed to fetch transcript for {video_id}: {e}")
            if "no element found" in str(e).lower() or "blocked" in str(e).lower():
                raise TranscriptException(
                    "YouTube blocked the request. Use a VPN or try again later.",
                    429,
                )
            raise TranscriptException(f"Failed: {str(e)}", 500)