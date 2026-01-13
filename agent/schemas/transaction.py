from pydantic import BaseModel, Field
from typing import List, Literal


class Transfer(BaseModel):
    sender_id: str = Field(..., description="ID from sender account")
    sender_entity: str = Field(..., description="Sender acoount entity")
    receiver_id: str = Field(..., description="ID from receiver account")
    receiver_entity: str = Field(..., description="Receiver acoount entity")
    currency: Literal["USD", "PYG"] = Field(..., description="Transaction currency")
    amount: str = Field(..., description="Transaction amount")
    
    
class TransferIn(BaseModel):
    sender_id: str = Field(..., description="ID from sender account")
    sender_entity: str = Field(..., description="Sender acoount entity")
    currency: Literal["USD", "PYG"] = Field(..., description="Transaction currency")
    amount: str = Field(..., description="Transaction amount")
    
    
class TransferOut(BaseModel):
    receiver_id: str = Field(..., description="ID from receiver account")
    receiver_entity: str = Field(..., description="Receiver acoount entity")
    currency: Literal["USD", "PYG"] = Field(..., description="Transaction currency")
    amount: str = Field(..., description="Transaction amount")
