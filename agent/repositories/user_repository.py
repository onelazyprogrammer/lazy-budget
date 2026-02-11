from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from agent.schemas.user import User, UserCreate, UserRead


class UserRepository:
    """Repository for user CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> Optional[UserRead]:
        """Fetch a user by username."""
        result = await self.session.execute(
            select(UserRead).where(UserRead.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[UserRead]:
        """Fetch a user by email."""
        result = await self.session.execute(
            select(UserRead).where(UserRead.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate, hashed_password: str) -> User:
        """Create a new user."""
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
