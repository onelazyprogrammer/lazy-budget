from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, Any, Annotated

class GraphState(BaseModel):
    messages: Annotated[list, add_messages]