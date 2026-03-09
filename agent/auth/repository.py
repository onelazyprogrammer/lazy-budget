from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from redis.asyncio import Redis

from agent.auth.schemas import User, UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate, hashed_password: str) -> User:
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


class TokenRepository:
    BLOCKLIST_PREFIX = "blocklist:"

    def __init__(self, redis: Redis):
        self.redis = redis

    async def blocklist_token(self, jti: str, ttl_seconds: int) -> None:
        key = f"{self.BLOCKLIST_PREFIX}{jti}"
        await self.redis.setex(key, ttl_seconds, "blocklisted")

    async def is_token_blocklisted(self, jti: str) -> bool:
        key = f"{self.BLOCKLIST_PREFIX}{jti}"
        return await self.redis.exists(key) > 0
