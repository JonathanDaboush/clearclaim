# Subscription model
class Subscription:
    def __init__(self, id: str, user_id: str, tier: str, start_date: str, end_date: str):
        """
        Subscription entity.
        Args:
            id (str): Subscription ID
            user_id (str): User ID
            tier (str): Subscription tier
            start_date (str): Start date UTC
            end_date (str): End date UTC
        """
        self.id = id
        self.user_id = user_id
        self.tier = tier
        self.start_date = start_date
        self.end_date = end_date
