from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.exceptions import DuplicateException
from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, RefreshRequest, TokenResponse, UserRegister, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=201, summary="Register a new user"
)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        return await AuthService(db).register(data)
    except DuplicateException as exc:
        raise HTTPException(status_code=409, detail=exc.message)


@router.post("/login", response_model=TokenResponse, summary="Obtain JWT access + refresh token")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).login(data)


@router.post("/refresh", response_model=TokenResponse, summary="Rotate refresh token")
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).refresh(body.refresh_token)


@router.post("/logout", status_code=204, summary="Revoke refresh token")
async def logout(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    await AuthService(db).logout(body.refresh_token)


@router.get("/me", response_model=UserResponse, summary="Get current authenticated user")
async def me(current_user: User = Depends(get_current_user)):
    return current_user
