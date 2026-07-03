from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateException
from app.core.logging_config import logger
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import LoginRequest, TokenResponse, UserRegister


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def register(self, data: UserRegister) -> User:
        existing = await self._get_by_email(data.email)
        if existing:
            raise DuplicateException("User", "email", data.email)

        user = User(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            role=data.role,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        logger.info("Registered user id=%d email=%s role=%s", user.id, user.email, user.role)
        return user

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self._get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

        token = create_access_token(subject=user.email, role=user.role.value)
        logger.info("Login success user=%s", user.email)
        return TokenResponse(access_token=token)

    async def _get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
