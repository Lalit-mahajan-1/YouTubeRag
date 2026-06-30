from typing import TypedDict


class AgentState(TypedDict):
    question: str
    playlist_id: str
    user_id: str
    video_summaries: list[dict]   # All videos in playlist
    selected_video_ids: list[str] # Picked by router
    retrieved_chunks: list[dict]  # From selected videos
    final_answer: str