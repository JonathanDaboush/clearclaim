# PaymentSQL class for payment DB operations
class PaymentSQL:
    def insert_payment(self, user_id: str, amount: float, method: str, metrics: dict, paid_at: str) -> str:
        """
        Insert payment record.
        Args:
            user_id (str): User ID
            amount (float): Payment amount
            method (str): Payment method
            metrics (dict): Payment metrics
            paid_at (str): UTC timestamp
        Returns:
            str: Payment ID
        """
        pass
