from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_auth_service, get_current_user
from app.db.models.user import User
from app.db.schemas.auth_schema import (
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthException, AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> RegisterResponse:
    try:
        return await auth_service.register(payload)
    except AuthException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        return await auth_service.login(payload)
    except AuthException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    payload: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        return await auth_service.refresh_tokens(payload.refresh_token)
    except AuthException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post("/logout", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def logout(current_user: User = Depends(get_current_user)) -> MessageResponse:
    return MessageResponse(message="Logged out successfully")