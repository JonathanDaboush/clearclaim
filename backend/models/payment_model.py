# Payment model
class Payment:
    def __init__(self, id, user_id, amount, method, metrics, paid_at):
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
