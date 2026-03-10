# SubscriptionRepository for PostgreSQL
class SubscriptionRepository:
    @staticmethod
    def insert_subscription(user_id: str, tier: str, start_date: str, end_date: str):
        """
        Insert subscription record.
        Args:
            user_id (str): User ID
            tier (str): Subscription tier
            start_date (str): Start date UTC
            end_date (str): End date UTC
        Returns:
            str: Subscription ID
        """
        pass

    @staticmethod
    def delete_subscription(subscription_id: str):
        """
        Delete subscription record.
        Args:
            subscription_id (str): Subscription ID
        Returns:
            bool: Success
        """
        pass
