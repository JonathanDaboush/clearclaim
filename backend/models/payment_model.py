    # ...existing code...
from typing import Dict, Any


class Payment:
    def __init__(self, id: str, user_id: str, amount: float, method: str, metrics: Dict[str, Any], paid_at: str):
        """
        Payment entity.
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

    def validate_payment(self, user_id: str, amount: float, method: str, metrics: Dict[str, Any]) -> bool:
        """
        Validate payment input.
        Returns True if amount > 0 and method is allowed.
        """
        allowed_methods = ['credit_card', 'bank_transfer', 'paypal']
        return amount > 0 and method in allowed_methods
