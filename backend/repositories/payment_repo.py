# PaymentRepository for PostgreSQL
class PaymentRepository:
    @staticmethod
    def insert_payment(user_id: str, amount: float, method: str, metrics: dict, paid_at: str):
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

    @staticmethod
    def delete_payment(payment_id: str):
        """
        Delete payment record.
        Args:
            payment_id (str): Payment ID
        Returns:
            bool: Success
        """
        pass
