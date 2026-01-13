from pydantic import BaseModel, Field, field_validator
from typing import Any, Literal, Optional, Union, List
import re


class TextPart(BaseModel):
    type: str = "text"
    text: str


class ImagePart(BaseModel):
    type: str = "image"
    base64: str
    mime_type: str


ContentPart = Union[TextPart, ImagePart]


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
    content: Union[str, List[ContentPart]] = Field(
        ..., description="The content of the message", min_length=1
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: Any) -> Any:
        """Validate the message content."""
        if isinstance(v, str):
            # Check for potentially harmful content
            if re.search(r"<script.*?>.*?</script>", v, re.IGNORECASE | re.DOTALL):
                raise ValueError("Content contains potentially harmful script tags")

            # Check for null bytes
            if "\0" in v:
                raise ValueError("Content contains null bytes")

        return v


class ChatRequest(BaseModel):
    messages: List[Message] = Field(
        ..., description="List of messages in the conversation"
    )


class ChatResponse(BaseModel):
    response: Optional[str] = Field(
        description="Response received from AI Agent", default=None
    )
