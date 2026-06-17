from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings
from app.core.logger import get_logger
from app.utils.youtube_parser import extract_video_id

logger = get_logger(__name__)


class TitleServiceException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class TitleService:
    @staticmethod
    async def get_title(youtube_url: str) -> str:
        """Fetch video title from YouTube Data API v3."""
        try:
            video_id = extract_video_id(youtube_url)
        except ValueError as e:
            raise TitleServiceException(str(e), 400)

        if not settings.YOUTUBE_API_KEY:
            logger.warning("YOUTUBE_API_KEY not configured — returning fallback title")
            return f"Video {video_id}"

        try:
            youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)
            request = youtube.videos().list(part="snippet", id=video_id)
            response = request.execute()

            items = response.get("items", [])
            if not items:
                logger.warning(f"No video found for ID: {video_id}")
                return f"Video {video_id}"

            title = items[0]["snippet"]["title"]
            logger.info(f"Fetched title for {video_id}: {title}")
            return title

        except HttpError as e:
            logger.error(f"YouTube API error for {video_id}: {e}")
            return f"Video {video_id}"

        except Exception as e:
            logger.error(f"Failed to fetch title for {video_id}: {e}")
            return f"Video {video_id}"