import uuid
import json
from typing import Any, Dict, List
import db


class PaymentRepository:

    @staticmethod
    def insert_payment(user_id: str, amount: float, method: str, metrics: Dict[str, Any], paid_at: str) -> str:
        payment_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO payments (id, user_id, amount, method, metrics) VALUES (%s, %s, %s, %s, %s)",
            (payment_id, user_id, amount, method, json.dumps(metrics) if isinstance(metrics, dict) else metrics),
        )
        return payment_id

    @staticmethod
    def delete_payment(payment_id: str) -> bool:
        rows = db.query("SELECT id FROM payments WHERE id = %s", (payment_id,))
        if not rows:
            return False
        db.execute("DELETE FROM payments WHERE id = %s", (payment_id,))
        return True

    @staticmethod
    def get_by_user(user_id: str) -> List[Dict[str, Any]]:
        return db.query(
            "SELECT id, user_id, amount, method, metrics, paid_at::text AS paid_at FROM payments WHERE user_id = %s ORDER BY paid_at",
            (user_id,),
        )
