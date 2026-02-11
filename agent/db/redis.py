import redis.asyncio as aioredis
from redis.asyncio import Redis

from agent.core.config import settings

redis_client: Redis | None = None


async def get_redis() -> Redis:
    """
    Get or create the shared async Redis client.

    Returns:
        The async Redis client instance.
    """
    global redis_client
    if redis_client is None:
        redis_client = aioredis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            decode_responses=True,
        )
    return redis_client


async def close_redis() -> None:
    """Gracefully close the Redis connection."""
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None
