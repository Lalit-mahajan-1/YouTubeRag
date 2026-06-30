from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_agent_service, get_current_user
from app.db.models.user import User
from app.db.schemas.agent_schema import AgentAskRequest, AgentAskResponse
from app.services.agent_service import AgentService, AgentServiceException

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/ask", response_model=AgentAskResponse)
async def ask_agent(
    payload: AgentAskRequest,
    user: User = Depends(get_current_user),
    service: AgentService = Depends(get_agent_service),
):
    try:
        return await service.ask(user.id, payload.playlist_id, payload.question)
    except AgentServiceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)