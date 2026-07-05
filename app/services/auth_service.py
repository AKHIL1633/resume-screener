from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateException
from app.core.logging_config import logger
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    refresh_token_expires_at,
    verify_password,
)
from app.models.token import RefreshToken
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

        access_token = create_access_token(subject=user.email, role=user.role.value)
        refresh_token_str = await self._create_refresh_token(user.id)
        await self.db.commit()
        logger.info("Login success user=%s", user.email)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token_str)

    async def refresh(self, refresh_token_str: str) -> TokenResponse:
        """Exchange a valid refresh token for a new access + refresh token pair."""
        token_hash = hash_token(refresh_token_str)
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked.is_(False),
            )
        )
        db_token: RefreshToken | None = result.scalar_one_or_none()

        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        if db_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
            )

        # Rotate: revoke old token
        db_token.is_revoked = True
        await self.db.flush()

        user_result = await self.db.execute(select(User).where(User.id == db_token.user_id))
        user: User | None = user_result.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

        access_token = create_access_token(subject=user.email, role=user.role.value)
        new_refresh_str = await self._create_refresh_token(user.id)
        await self.db.commit()
        logger.info("Token refreshed for user=%s", user.email)
        return TokenResponse(access_token=access_token, refresh_token=new_refresh_str)

    async def logout(self, refresh_token_str: str) -> None:
        """Revoke the given refresh token."""
        token_hash = hash_token(refresh_token_str)
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        db_token: RefreshToken | None = result.scalar_one_or_none()
        if db_token and not db_token.is_revoked:
            db_token.is_revoked = True
            await self.db.commit()
            logger.info("Logout: revoked refresh token hash=%s…", token_hash[:8])

    async def _create_refresh_token(self, user_id: int) -> str:
        plain = generate_refresh_token()
        db_token = RefreshToken(
            user_id=user_id,
            token_hash=hash_token(plain),
            expires_at=refresh_token_expires_at(),
        )
        self.db.add(db_token)
        # caller must commit
        return plain

    async def _get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
