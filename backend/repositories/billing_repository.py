import uuid
import json
from typing import Any, Dict, List
import db


class BillingRepository:

    def create_subscription(self, user_id: str, tier: str) -> str:
        subscription_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO subscriptions (id, user_id, tier, start_date, end_date) VALUES (%s, %s, %s, '', '')",
            (subscription_id, user_id, tier),
        )
        return subscription_id

    def cancel_subscription(self, user_id: str) -> bool:
        rows = db.query(
            "SELECT id FROM subscriptions WHERE user_id = %s AND status = 'active' LIMIT 1",
            (user_id,),
        )
        if not rows:
            return False
        db.execute("UPDATE subscriptions SET status = 'cancelled' WHERE id = %s", (rows[0]["id"],))
        return True

    def update_subscription_status(self, user_id: str, status: str) -> bool:
        rows = db.query("SELECT id FROM subscriptions WHERE user_id = %s LIMIT 1", (user_id,))
        if not rows:
            return False
        db.execute("UPDATE subscriptions SET status = %s WHERE id = %s", (status, rows[0]["id"]))
        return True

    def record_payment(self, user_id: str, amount: float, method: str) -> str:
        payment_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO payments (id, user_id, amount, method) VALUES (%s, %s, %s, %s)",
            (payment_id, user_id, amount, method),
        )
        return payment_id

    def get_payment_history(self, user_id: str) -> List[Dict[str, Any]]:
        return db.query(
            "SELECT id, user_id, amount, method, metrics, paid_at::text AS paid_at FROM payments WHERE user_id = %s ORDER BY paid_at",
            (user_id,),
        )

    def generate_billing_metrics(self, user_id: str) -> Dict[str, Any]:
        total_row = db.query(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE user_id = %s",
            (user_id,),
        )
        total_paid = float(total_row[0]["total"]) if total_row else 0.0
        sub_row = db.query(
            "SELECT COUNT(*) AS cnt FROM subscriptions WHERE user_id = %s",
            (user_id,),
        )
        subscription_count = int(sub_row[0]["cnt"]) if sub_row else 0
        return {"total_paid": total_paid, "subscriptions": subscription_count}
