from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user, get_rag_service
from app.db.models.user import User
from app.db.schemas.rag_schema import AskQuestionRequest, AskQuestionResponse
from app.services.rag_service import RAGService, RAGServiceException

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ask", response_model=AskQuestionResponse)
async def ask_question(
    payload: AskQuestionRequest,
    user: User = Depends(get_current_user),
    service: RAGService = Depends(get_rag_service),
):
    try:
        result = await service.ask_question(user.id, payload.chat_id, payload.question)
        return AskQuestionResponse(**result)
    except RAGServiceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)