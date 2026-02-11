from redis.asyncio import Redis


class TokenRepository:
    """Repository for managing token blocklist operations in Redis."""

    BLOCKLIST_PREFIX = "blocklist:"

    def __init__(self, redis: Redis):
        self.redis = redis

    async def blocklist_token(self, jti: str, ttl_seconds: int) -> None:
        """
        Add a token to the blocklist.

        The key auto-expires after ttl_seconds, so entries are cleaned up
        once the original token would have expired anyway.

        Args:
            jti: The unique JWT ID to blocklist.
            ttl_seconds: Time-to-live in seconds (remaining token lifetime).
        """
        key = f"{self.BLOCKLIST_PREFIX}{jti}"
        await self.redis.setex(key, ttl_seconds, "blocklisted")

    async def is_token_blocklisted(self, jti: str) -> bool:
        """
        Check if a token is blocklisted.

        Args:
            jti: The unique JWT ID to check.

        Returns:
            True if the token is blocklisted, False otherwise.
        """
        key = f"{self.BLOCKLIST_PREFIX}{jti}"
        return await self.redis.exists(key) > 0
