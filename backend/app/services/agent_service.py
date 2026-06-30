import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import agent_graph
from app.core.logger import get_logger
from app.db.schemas.agent_schema import AgentAskResponse, AgentSource
from app.repositories.playlist_repository import PlaylistRepository

logger = get_logger(__name__)


class AgentServiceException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.playlist_repo = PlaylistRepository(db)

    async def ask(
        self,
        user_id: uuid.UUID,
        playlist_id: uuid.UUID,
        question: str,
    ) -> AgentAskResponse:
        # 1. Verify playlist ownership
        playlist = await self.playlist_repo.get_by_id(playlist_id, user_id)
        if not playlist:
            raise AgentServiceException("Playlist not found", 404)

        if not playlist.video_summaries:
            raise AgentServiceException(
                "Playlist has no processed videos", 400
            )

        # 2. Run agent workflow
        try:
            initial_state = {
                "question": question,
                "playlist_id": str(playlist_id),
                "user_id": str(user_id),
                "video_summaries": playlist.video_summaries,
                "selected_video_ids": [],
                "retrieved_chunks": [],
                "final_answer": "",
            }

            final_state = await agent_graph.ainvoke(initial_state)

            # 3. Build source list
            selected_sources = []
            for vid_id in final_state["selected_video_ids"]:
                video = next(
                    (
                        v
                        for v in playlist.video_summaries
                        if v["video_id"] == vid_id
                    ),
                    None,
                )
                if video:
                    selected_sources.append(
                        AgentSource(
                            video_id=vid_id,
                            video_title=video["title"],
                        )
                    )

            return AgentAskResponse(
                answer=final_state["final_answer"],
                selected_videos=selected_sources,
                total_chunks_used=len(final_state["retrieved_chunks"]),
            )

        except Exception as e:
            logger.error(f"Agent failed: {e}")
            raise AgentServiceException(f"Agent failed: {str(e)}", 500)