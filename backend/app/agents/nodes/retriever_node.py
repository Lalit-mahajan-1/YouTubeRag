import asyncio

from app.agents.state import AgentState
from app.core.logger import get_logger
from app.services.embedding_service import embedding_service

logger = get_logger(__name__)

TOP_K_PER_VIDEO = 5


async def retriever_node(state: AgentState) -> dict:
    """Retrieves top chunks from each selected video in parallel."""

    selected_ids = state["selected_video_ids"]
    user_id = state["user_id"]
    question = state["question"]
    video_summaries = state["video_summaries"]

    if not selected_ids:
        return {"retrieved_chunks": []}

    # Build map: video_id (UUID) → youtube_id
    id_to_yt = {v["video_id"]: v["youtube_id"] for v in video_summaries}

    async def fetch_from_video(video_id: str) -> list[dict]:
        youtube_id = id_to_yt.get(video_id)
        if not youtube_id:
            logger.warning(f"No youtube_id found for {video_id}")
            return []

        # ✅ Use youtube_id in namespace (matches Pinecone storage)
        namespace = f"user_{user_id}_video_{youtube_id}"

        try:
            vector_store = embedding_service.get_vector_store(namespace)
            docs = await asyncio.to_thread(
                lambda: vector_store.similarity_search(
                    question, k=TOP_K_PER_VIDEO
                )
            )

            video_title = next(
                (
                    v["title"]
                    for v in video_summaries
                    if v["video_id"] == video_id
                ),
                "Unknown",
            )

            logger.info(f"Retrieved {len(docs)} chunks from {youtube_id}")

            return [
                {
                    "content": d.page_content,
                    "video_id": video_id,
                    "video_title": video_title,
                }
                for d in docs
            ]
        except Exception as e:
            logger.error(f"Retrieval failed for {video_id}: {e}")
            return []

    results = await asyncio.gather(*[fetch_from_video(vid) for vid in selected_ids])
    all_chunks = [chunk for video_chunks in results for chunk in video_chunks]

    logger.info(
        f"Total: {len(all_chunks)} chunks from {len(selected_ids)} videos"
    )
    return {"retrieved_chunks": all_chunks}