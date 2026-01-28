from fastapi import APIRouter

from agent.api.files import router as files_router
from agent.api.chat import router as chat_router
from agent.api.auth import router as auth_router

api_router = APIRouter()
api_router.include_router(files_router, prefix="/files", tags=["files"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
