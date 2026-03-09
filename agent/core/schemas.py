from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Any, Union, List, Annotated
import re


class GraphState(BaseModel):
    messages: Annotated[list, add_messages]


class ContentPart(BaseModel):
    type: str


class TextPart(ContentPart):
    type: Literal["text"] = "text"
    text: str


class ImagePart(ContentPart):
    type: Literal["image"] = "image"
    base64: str
    mime_type: str


class FilePart(ContentPart):
    type: Literal["file"] = "file"
    filename: str
    mime_type: str
    base64: str


AnyContentPart = Union[
    TextPart,
    ImagePart,
    FilePart,
]


class Message(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(
        ..., description="The role of the message sender"
    )
    content: List[AnyContentPart] = Field(
        ..., description="The content of the message", min_length=1
    )

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, v: Any) -> Any:
        if isinstance(v, str):
            if re.search(r"<script.*?>.*?</script>", v, re.IGNORECASE | re.DOTALL):
                raise ValueError("Content contains potentially harmful script tags")
            if "\0" in v:
                raise ValueError("Content contains null bytes")
            return [{"type": "text", "text": v}]
        return v
