import jwt
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from agent.auth.schemas import Token, TokenData, User, UserCreate, UserRead
from agent.auth.repository import UserRepository, TokenRepository
from agent.auth.utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    is_token_expired,
)
from agent.core.config import settings
from agent.db.database import get_db
from agent.db.redis import get_redis

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> User | None:
    repo = UserRepository(db)
    user = await repo.get_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# =============================================================================
# Dependencies
# =============================================================================


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )

        token_expiration = payload.get("exp")

        if is_token_expired(token_expiration):
            raise credentials_exception

        jti: str | None = payload.get("jti")
        if jti is None:
            raise credentials_exception

        redis = await get_redis()
        token_repo = TokenRepository(redis)
        if await token_repo.is_token_blocklisted(jti):
            raise credentials_exception

        username: str | None = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception

    repo = UserRepository(db)
    user = await repo.get_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# =============================================================================
# Endpoints
# =============================================================================


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    repo = UserRepository(db)

    existing_user = await repo.get_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    existing_email = await repo.get_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(user_data.password)
    user = await repo.create(user_data, hashed_password)
    return user


@router.post("/token", response_model=UserRead)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return UserRead(**user.model_dump(), token=access_token)


@router.post("/logout")
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    payload = jwt.decode(
        token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )
    jti = payload.get("jti")
    exp = payload.get("exp")

    exp_datetime = datetime.fromtimestamp(exp, timezone.utc)
    now = datetime.now(timezone.utc)
    ttl_seconds = int((exp_datetime - now).total_seconds())

    if ttl_seconds > 0:
        redis = await get_redis()
        token_repo = TokenRepository(redis)
        await token_repo.blocklist_token(jti, ttl_seconds)

    return {"detail": "Successfully logged out"}


@router.get("/users/me", response_model=UserRead)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserRead:
    access_token = create_access_token(data={"sub": current_user.username})
    return UserRead(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        disabled=current_user.disabled,
        created_at=current_user.created_at,
        token=access_token,
    )
