from fastapi import FastAPI
from agent.middleware import LoggingMiddleware
from agent.utils.logging import setup_logging
from contextlib import asynccontextmanager
from sqlmodel import SQLModel

from agent.db.database import engine
from agent.db.redis import get_redis, close_redis
from agent.auth.router import router as auth_router
from agent.chat.router import router as chat_router
from agent.files.router import router as files_router

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    await get_redis()
    yield
    await close_redis()
    await engine.dispose()


app = FastAPI(title="Lazy Budget API", lifespan=lifespan)

app.add_middleware(LoggingMiddleware)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(files_router, prefix="/api/v1/files", tags=["files"])


@app.get("/")
def read_root():
    return {"message": "Lazy Budget API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("agent.main:app", host="0.0.0.0", port=8000, reload=True)
