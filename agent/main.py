from fastapi import FastAPI
from agent.api.api import api_router
from agent.middleware import LoggingMiddleware
from agent.utils.logging import setup_logging
from contextlib import asynccontextmanager
from sqlmodel import SQLModel

from agent.db.database import engine
from agent.db.redis import get_redis, close_redis

# Configure logging at startup
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    # Startup: Connect to Redis
    await get_redis()
    yield
    # Shutdown: Close Redis connection
    await close_redis()
    # Shutdown: Dispose engine
    await engine.dispose()


app = FastAPI(title="Lazy Budget API", lifespan=lifespan)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Lazy Budget API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("agent.main:app", host="0.0.0.0", port=8000, reload=True)
