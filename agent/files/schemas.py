from pydantic import BaseModel, Field, field_validator
from typing import Literal, List, Optional


class Transfer(BaseModel):
    sender: Optional[str] = Field(..., description="Nombre del ordenante")
    sender_bank: Optional[str] = Field(..., description="Banco del ordenante")

    receiver: Optional[str] = Field(..., description="Nombre del beneficiario")
    receiver_bank: Optional[str] = Field(..., description="Banco del beneficiario")

    currency: Literal["PYG", "USD", "ARS"] = Field(
        ..., description="Moneda de la transferencia", examples=["PYG", "USD", "ARS"]
    )
    amount: Optional[float] = Field(..., description="Monto de la transferencia")
    reason: Optional[str] = Field(None, description="Motivo/razón de la transferencia")
    date: Optional[str] = Field(
        ...,
        description="Fecha de la transferencia (YYYY-MM-DD)",
        examples=["2024-01-13"],
    )

    @field_validator(
        "sender",
        "sender_bank",
        "receiver",
        "receiver_bank",
        "currency",
        "reason",
        "date",
    )
    def uppercase_strings(cls, v: str) -> str:
        return v.upper()


class Transactions(BaseModel):
    transactions: List[Transfer]


class ImageAnalysis(BaseModel):
    summary: str
    detected_objects: List[str]
    is_receipt: bool
    currency: Optional[str] = None
    total_amount: Optional[float] = None
    date: Optional[str] = None
