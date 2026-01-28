from pydantic import BaseModel
from typing import List, Optional


class ImageAnalysis(BaseModel):
    summary: str
    detected_objects: List[str]
    is_receipt: bool
    currency: Optional[str] = None
    total_amount: Optional[float] = None
    date: Optional[str] = None
