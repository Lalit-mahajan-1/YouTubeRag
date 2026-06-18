import re
import httpx

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


PLAYLIST_ID_PATTERN = re.compile(r"list=([a-zA-Z0-9_-]+)")


def extract_playlist_id(url: str) -> str:
    """Extracts playlist ID from YouTube playlist URL."""
    match = PLAYLIST_ID_PATTERN.search(url)
    if not match:
        raise ValueError("Invalid YouTube playlist URL")
    return match.group(1)


def fetch_playlist_videos(playlist_url: str) -> tuple[str, list[dict]]:
    """
    Fetches all videos from a playlist using YouTube Data API v3.

    Returns:
        (playlist_title, [{"video_id": "...", "title": "...", "url": "..."}, ...])
    """
    if not settings.YOUTUBE_API_KEY:
        raise ValueError("YOUTUBE_API_KEY not configured")

    playlist_id = extract_playlist_id(playlist_url)

    try:
        # 1. Fetch playlist title
        playlist_title = _fetch_playlist_title(playlist_id)

        # 2. Fetch all videos (with pagination)
        videos = _fetch_all_videos(playlist_id)

        logger.info(f"Found {len(videos)} videos in playlist {playlist_id}")
        return playlist_title, videos

    except Exception as e:
        logger.error(f"Failed to fetch playlist: {e}")
        raise ValueError(f"Failed to fetch playlist: {str(e)}")


def _fetch_playlist_title(playlist_id: str) -> str:
    """Get playlist title from YouTube API."""
    url = "https://www.googleapis.com/youtube/v3/playlists"
    params = {
        "part": "snippet",
        "id": playlist_id,
        "key": settings.YOUTUBE_API_KEY,
    }

    response = httpx.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    items = data.get("items", [])
    if not items:
        return "Untitled Playlist"

    return items[0]["snippet"]["title"]


def _fetch_all_videos(playlist_id: str) -> list[dict]:
    """Fetch all videos in playlist with pagination."""
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    videos = []
    page_token = None

    while True:
        params = {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50,
            "key": settings.YOUTUBE_API_KEY,
        }
        if page_token:
            params["pageToken"] = page_token

        response = httpx.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        for item in data.get("items", []):
            video_id = item["contentDetails"]["videoId"]
            videos.append(
                {
                    "video_id": video_id,
                    "title": item["snippet"]["title"],
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                }
            )

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return videos