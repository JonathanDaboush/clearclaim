import uuid
from typing import List, Dict, Any
from models.payment_model import Payment


class PaymentRepository:
    _payments: List[Payment] = []  # In-memory (replace with DB in production)

    @staticmethod
    def insert_payment(user_id: str, amount: float, method: str, metrics: Dict[str, Any], paid_at: str) -> str:
        """Record a payment transaction. Returns the new payment ID."""
        payment_id = str(uuid.uuid4())
        PaymentRepository._payments.append(Payment(
            id=payment_id,
            user_id=user_id,
            amount=amount,
            method=method,
            metrics=metrics,
            paid_at=paid_at,
        ))
        return payment_id

    @staticmethod
    def delete_payment(payment_id: str) -> bool:
        """Remove a payment record. Returns True if found."""
        for p in PaymentRepository._payments:
            if p.id == payment_id:
                PaymentRepository._payments.remove(p)
                return True
        return False
