from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ErrorMessages
from app.core.logger import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.models.user import User
from app.db.schemas.auth_schema import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
)
from app.repositories.user_repository import UserRepository

logger = get_logger(__name__)


class AuthException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, data: RegisterRequest) -> RegisterResponse:
        if await self.user_repo.email_exists(data.email):
            raise AuthException(ErrorMessages.USER_ALREADY_EXISTS, 409)

        if await self.user_repo.username_exists(data.username):
            raise AuthException("Username already taken", 409)

        hashed = hash_password(data.password)
        user = await self.user_repo.create(
            email=data.email,
            username=data.username,
            hashed_password=hashed,
        )

        logger.info(f"New user registered: {user.email}")

        return RegisterResponse(
            message="Registration successful",
            user=UserResponse.model_validate(user),
        )

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(data.email)

        if not user or not verify_password(data.password, user.hashed_password):
            raise AuthException(ErrorMessages.INVALID_CREDENTIALS, 401)

        if not user.is_active:
            raise AuthException(ErrorMessages.INACTIVE_USER, 403)

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        logger.info(f"User logged in: {user.email}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            raise AuthException(ErrorMessages.INVALID_TOKEN, 401)

        user = await self.user_repo.get_by_id(payload["sub"])

        if not user:
            raise AuthException(ErrorMessages.USER_NOT_FOUND, 404)

        if not user.is_active:
            raise AuthException(ErrorMessages.INACTIVE_USER, 403)

        new_access_token = create_access_token(str(user.id))
        new_refresh_token = create_refresh_token(str(user.id))

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )

    async def get_current_user(self, token: str) -> User:
        payload = decode_token(token)

        if not payload or payload.get("type") != "access":
            raise AuthException(ErrorMessages.INVALID_TOKEN, 401)

        user = await self.user_repo.get_by_id(payload["sub"])

        if not user:
            raise AuthException(ErrorMessages.USER_NOT_FOUND, 404)

        if not user.is_active:
            raise AuthException(ErrorMessages.INACTIVE_USER, 403)

        return user