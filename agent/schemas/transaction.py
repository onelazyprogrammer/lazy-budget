from pydantic import BaseModel, Field
from typing import Literal
from datetime import date


class Transfer(BaseModel):
    sender: str = Field(..., description="Sender acoount entity")
    sender_type: Literal["user", "business"] = Field(..., description="Sender type")
    sender_bank: str = Field(..., description="Sender bank")

    receiver: str = Field(..., description="Receiver acoount entity")
    receiver_type: Literal["user", "business"] = Field(..., description="Receiver type")
    receiver_bank: str = Field(..., description="Receiver bank")

    currency: Literal["PYG", "USD", "ARS"] = Field(
        ..., description="Transaction currency", examples=["PYG", "USD", "ARS"]
    )
    amount: float = Field(..., description="Transaction amount")
    reason: str = Field(..., description="Transaction reason")
    date: date = Field(..., description="Transaction date")
