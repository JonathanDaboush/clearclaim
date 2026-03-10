import uuid
from typing import List
from models.subscription_model import Subscription


class SubscriptionRepository:
    _subscriptions: List[Subscription] = []  # In-memory (replace with DB in production)

    @staticmethod
    def insert_subscription(user_id: str, tier: str, start_date: str, end_date: str) -> str:
        """Create a subscription record for a user. Returns the new subscription ID."""
        subscription_id = str(uuid.uuid4())
        SubscriptionRepository._subscriptions.append(Subscription(
            id=subscription_id,
            user_id=user_id,
            tier=tier,
            start_date=start_date,
            end_date=end_date,
        ))
        return subscription_id

    @staticmethod
    def delete_subscription(subscription_id: str) -> bool:
        """Remove a subscription record. Returns True if found."""
        for sub in SubscriptionRepository._subscriptions:
            if sub.id == subscription_id:
                SubscriptionRepository._subscriptions.remove(sub)
                return True
        return False
