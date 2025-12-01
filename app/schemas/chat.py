from pydantic import BaseModel, Field, field_validator
from typing import Any, Literal, Optional
import re


class Message(BaseModel):
    """Message model for chat endpoint.

    Attributes:
        role: The role of the message sender (user or assistant).
        content: The content of the message.
    """

    model_config = {"extra": "ignore"}

    role: Literal["user", "assistant", "system"] = Field(
        ..., description="The role of the message sender"
    )
    content: str = Field(
        ..., description="The content of the message", min_length=1
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate the message content.

        Args:
            v: The content to validate

        Returns:
            str: The validated content

        Raises:
            ValueError: If the content contains disallowed patterns
        """
        # Check for potentially harmful content
        if re.search(r"<script.*?>.*?</script>", v, re.IGNORECASE | re.DOTALL):
            raise ValueError("Content contains potentially harmful script tags")

        # Check for null bytes
        if "\0" in v:
            raise ValueError("Content contains null bytes")

        return v


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="User session ID")
    user_id: Optional[str] = Field(description="User ID")
    text: str = Field(..., description="User message")


class ChatResponse(BaseModel):
    response: Optional[str] = Field(
        description="Response received from AI Agent", default=None
    )
    intent: Optional[Any] = Field(
        description="Intent to be sent to the sdk", default=None
    )


class ConversationRequest(BaseModel):
    user_id: Optional[str] = Field(description="User ID")
    session_id: str = Field(..., description="User session ID")
    messages: list[Message] = Field(..., description="Message history")


class ConversationResponse(BaseModel):
    session_id: str = Field(..., description="User session ID")
    user_id: Optional[str] = Field(description="User ID")
    messages: list[Message] = Field(
        ..., description="Message history + latest generated message"
    )