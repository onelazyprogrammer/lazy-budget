from pydantic import BaseModel, Field
from typing import List, Optional

from agent.core.schemas import Message


class ChatRequest(BaseModel):
    messages: List[Message] = Field(
        ..., description="List of messages in the conversation"
    )


class ChatResponse(BaseModel):
    response: Optional[str] = Field(
        description="Response received from AI Agent", default=None
    )
