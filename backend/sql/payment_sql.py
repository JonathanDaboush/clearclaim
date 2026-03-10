import uuid
from typing import Dict, Any


class PaymentSQL:
    def insert_payment(self, user_id: str, amount: float, method: str, metrics: Dict[str, Any], paid_at: str) -> str:
        """Return the SQL insert values for a payment record. Returns new payment ID."""
        return str(uuid.uuid4())  # In production: delegate to SQLTemplate.insert(...)
