# PaymentDB for persistence mapping
from typing import Dict, Any


class PaymentDB:
    def __init__(self, id: str, user_id: str, amount: float, method: str, metrics: Dict[str, Any], paid_at: str):
        """
        Persistence model for DB operations.
        Args:
            id (str): Payment ID
            user_id (str): User ID
            amount (float): Payment amount
            method (str): Payment method
            metrics (dict): Payment metrics
            paid_at (str): UTC timestamp
        """
        self.id = id
        self.user_id = user_id
        self.amount = amount
        self.method = method
        self.metrics = metrics
        self.paid_at = paid_at
