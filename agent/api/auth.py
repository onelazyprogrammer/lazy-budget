import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from agent.schemas.auth import Token, TokenData
from agent.core.config import settings
from agent.db.database import get_db
from agent.schemas.user import User, UserCreate, UserRead
from agent.repositories.user_repository import UserRepository
from agent.utils.auth import verify_password, get_password_hash, create_access_token, is_token_expired

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> User | None:
    """
    Authenticate a user by username and password.

    Args:
        db: Database session
        username: User's username
        password: Plain text password

    Returns:
        User object if authentication succeeds, None otherwise
    """
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
    """
    FastAPI dependency to get the current authenticated user from JWT token.

    This dependency:
    1. Extracts the JWT token from the Authorization header
    2. Decodes and validates the token
    3. Fetches the user from the database

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
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
    """
    FastAPI dependency to get the current active (non-disabled) user.

    Raises:
        HTTPException: 400 if user is disabled
    """
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
    """
    Register a new user.

    Creates a new user account with the provided credentials.
    The password is hashed before storage.

    Args:
        user_data: User registration data (username, email, password, full_name)
        db: Database session

    Returns:
        Created user data (without password)

    Raises:
        HTTPException: 400 if username or email already exists
    """
    repo = UserRepository(db)

    # Check if username already exists
    existing_user = await repo.get_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    existing_email = await repo.get_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user with hashed password
    hashed_password = get_password_hash(user_data.password)
    user = await repo.create(user_data, hashed_password)
    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    OAuth2 compatible token login endpoint.

    Authenticates user with username and password, returns JWT access token.

    Args:
        form_data: OAuth2 password request form (username, password)
        db: Database session

    Returns:
        Token object with access_token and token_type

    Raises:
        HTTPException: 401 if credentials are incorrect
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me/", response_model=UserRead)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Get current authenticated user's information.

    Requires a valid JWT token in the Authorization header.

    Returns:
        Current user's data
    """
    return current_user
