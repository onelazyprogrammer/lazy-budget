from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from agent.core.config import settings

_pool: AsyncConnectionPool | None = None
_checkpointer: AsyncPostgresSaver | None = None


async def open_checkpointer() -> AsyncPostgresSaver:
    global _pool, _checkpointer
    _pool = AsyncConnectionPool(conninfo=settings.checkpoint_url, max_size=10, open=False)
    await _pool.open()
    _checkpointer = AsyncPostgresSaver(_pool)
    await _checkpointer.setup()
    return _checkpointer


async def close_checkpointer() -> None:
    global _pool, _checkpointer
    if _pool is not None:
        await _pool.close()
    _pool = None
    _checkpointer = None


def get_checkpointer() -> AsyncPostgresSaver:
    if _checkpointer is None:
        raise RuntimeError("Checkpointer not initialized")
    return _checkpointer
