import uuid
import datetime
from typing import List, Dict, Any


class BillingRepository:
    _subscriptions: List[Dict[str, Any]] = []  # In-memory (replace with DB in production)
    _payments: List[Dict[str, Any]] = []       # In-memory (replace with DB in production)

    def create_subscription(self, user_id: str, tier: str) -> str:
        """Create a subscription record. Returns the new subscription ID."""
        subscription_id = str(uuid.uuid4())
        self._subscriptions.append({
            "id": subscription_id,
            "user_id": user_id,
            "tier": tier,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "active",
        })
        return subscription_id

    def cancel_subscription(self, user_id: str) -> bool:
        """Mark the user's active subscription as cancelled. Returns True if found."""
        for sub in self._subscriptions:
            if sub["user_id"] == user_id and sub["status"] == "active":
                sub["status"] = "cancelled"
                return True
        return False

    def update_subscription_status(self, user_id: str, status: str) -> bool:
        """Update a user's subscription status. Returns True if found."""
        for sub in self._subscriptions:
            if sub["user_id"] == user_id:
                sub["status"] = status
                return True
        return False

    def record_payment(self, user_id: str, amount: float, method: str) -> str:
        """Record a payment for the user. Returns the new payment ID."""
        payment_id = str(uuid.uuid4())
        self._payments.append({
            "id": payment_id,
            "user_id": user_id,
            "amount": amount,
            "method": method,
            "paid_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        })
        return payment_id

    def get_payment_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Return all payment records for the user."""
        return [p for p in self._payments if p["user_id"] == user_id]

    def generate_billing_metrics(self, user_id: str) -> Dict[str, Any]:
        """Return total amount paid and subscription count for the user."""
        total_paid = sum(p["amount"] for p in self._payments if p["user_id"] == user_id)
        subscription_count = len([s for s in self._subscriptions if s["user_id"] == user_id])
        return {"total_paid": total_paid, "subscriptions": subscription_count}
