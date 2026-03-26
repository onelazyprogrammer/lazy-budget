import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from agent.auth.router import get_current_active_user
from agent.auth.schemas import User
from agent.chat.repository import ConversationRepository
from agent.chat.schemas import (
    ConversationCreate,
    ConversationHistory,
    ConversationRead,
    MessageRequest,
)
from agent.core.schemas import Message
from agent.core.agent import agent
from agent.db.database import get_db

router = APIRouter()


@router.post("/conversations", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    body: ConversationCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
) -> ConversationRead:
    repo = ConversationRepository(db)
    conversation = await repo.create(user_id=current_user.id, title=body.title)
    return ConversationRead(**conversation.model_dump())


@router.get("/conversations", response_model=list[ConversationRead])
async def list_conversations(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
) -> list[ConversationRead]:
    repo = ConversationRepository(db)
    conversations = await repo.list_by_user(user_id=current_user.id)
    return [ConversationRead(**c.model_dump()) for c in conversations]


@router.get("/conversations/{conversation_id}", response_model=ConversationHistory)
async def get_conversation_history(
    conversation_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
) -> ConversationHistory:
    repo = ConversationRepository(db)
    try:
        cid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    conversation = await repo.get_by_id_and_user(conversation_id=cid, user_id=current_user.id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    messages = await agent.get_history(thread_id=str(conversation.id))
    return ConversationHistory(
        conversation=ConversationRead(**conversation.model_dump()),
        messages=messages,
    )


@router.post("/conversations/{conversation_id}/messages", response_model=list[Message])
async def send_message(
    conversation_id: str,
    body: MessageRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    repo = ConversationRepository(db)
    try:
        cid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    conversation = await repo.get_by_id_and_user(conversation_id=cid, user_id=current_user.id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    return await agent.get_response(thread_id=str(conversation.id), user_message=body.message)
