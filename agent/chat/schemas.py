import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
from sqlmodel import SQLModel, Field

from agent.core.schemas import Message


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationCreate(BaseModel):
    title: str


class ConversationRead(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime


class MessageRequest(BaseModel):
    message: Message


class ConversationHistory(BaseModel):
    conversation: ConversationRead
    messages: List[Message]
