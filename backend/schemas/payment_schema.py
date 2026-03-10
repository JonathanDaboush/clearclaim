# PaymentSchema for serialization and type checking
from pydantic import BaseModel
from typing import Dict

class PaymentSchema(BaseModel):
    id: str
    user_id: str
    amount: float
    method: str
    metrics: Dict
    paid_at: str
