import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_current_user, get_notes_service
from app.db.models.user import User
from app.db.schemas.notes_schema import NotesGenerationResponse
from app.services.notes_service import NotesService, NotesServiceException

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.get("/{video_id}", response_model=NotesGenerationResponse)
async def get_notes(
    video_id: uuid.UUID,
    user: User = Depends(get_current_user),
    service: NotesService = Depends(get_notes_service),
):
    """Generate markdown notes for a video (JSON response)."""
    try:
        notes = await service.generate_notes(user.id, video_id)
        return NotesGenerationResponse(
            message="Notes generated successfully",
            notes=notes,
        )
    except NotesServiceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{video_id}/pdf")
async def download_notes_pdf(
    video_id: uuid.UUID,
    user: User = Depends(get_current_user),
    service: NotesService = Depends(get_notes_service),
):
    """Generate notes and return as downloadable PDF."""
    try:
        pdf_bytes, filename = await service.generate_notes_pdf(user.id, video_id)

        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )
    except NotesServiceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)