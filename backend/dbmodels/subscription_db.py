# SubscriptionDB for persistence mapping
class SubscriptionDB:
    def __init__(self, id, user_id, tier, start_date, end_date):
        """
        Persistence model for DB operations.
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
