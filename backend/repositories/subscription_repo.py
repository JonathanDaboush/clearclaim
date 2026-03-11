import uuid
from typing import Any, Dict, List
import db


class SubscriptionRepository:

    @staticmethod
    def insert_subscription(user_id: str, tier: str, start_date: str, end_date: str) -> str:
        subscription_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO subscriptions (id, user_id, tier, start_date, end_date) VALUES (%s, %s, %s, %s, %s)",
            (subscription_id, user_id, tier, start_date, end_date),
        )
        return subscription_id

    @staticmethod
    def delete_subscription(subscription_id: str) -> bool:
        rows = db.query("SELECT id FROM subscriptions WHERE id = %s", (subscription_id,))
        if not rows:
            return False
        db.execute("DELETE FROM subscriptions WHERE id = %s", (subscription_id,))
        return True

    @staticmethod
    def get_by_user(user_id: str) -> List[Dict[str, Any]]:
        return db.query(
            "SELECT id, user_id, tier, start_date, end_date, status, created_at::text AS created_at FROM subscriptions WHERE user_id = %s ORDER BY created_at",
            (user_id,),
        )
