from repositories.billing_repository import BillingRepository
from services.audit_service import AuditService
from services.notification_service import NotificationService
from typing import List, Dict, Any


class BillingService:
    def __init__(self):
        self._repo = BillingRepository()

    def create_subscription(self, user_id: str, tier: str) -> Dict[str, Any]:
        """Create a new subscription for the user. Logs and notifies."""
        subscription_id = self._repo.create_subscription(user_id, tier)
        AuditService().log_event("create_subscription", user_id, {"tier": tier})
        NotificationService().create_notification(user_id, "subscription_created", f"Subscription created: {tier}.")
        return {"status": "Subscription created", "subscription_id": subscription_id}

    def cancel_subscription(self, user_id: str) -> Dict[str, Any]:
        """Cancel the user's active subscription. Logs and notifies."""
        self._repo.cancel_subscription(user_id)
        AuditService().log_event("cancel_subscription", user_id, {})
        NotificationService().create_notification(user_id, "subscription_cancelled", "Your subscription has been cancelled.")
        return {"status": "Subscription cancelled"}

    def update_subscription_status(self, user_id: str, status: str) -> Dict[str, Any]:
        """Update a user's subscription status. Logs and notifies."""
        self._repo.update_subscription_status(user_id, status)
        AuditService().log_event("update_subscription_status", user_id, {"status": status})
        NotificationService().create_notification(user_id, "subscription_status_updated", f"Subscription status updated to {status}.")
        return {"status": "Subscription updated"}

    def record_payment(self, user_id: str, amount: float, method: str, idempotency_key: str = '') -> Dict[str, Any]:
        """Record a payment transaction. Idempotency key prevents duplicate charges on retries."""
        from utils.validators import validate_payment, validate_idempotency_key, ValidationError
        try:
            validate_payment(amount, method)
            validate_idempotency_key(idempotency_key)
        except ValidationError as exc:
            return {"status": "error", "message": str(exc)}
        from utils.idempotency import idempotency_guard, store_idempotency_result
        try:
            cached = idempotency_guard(idempotency_key, endpoint="/billing/record_payment", user_id=user_id)
            if cached is not None:
                return cached
        except ValueError as exc:
            return {"status": "error", "message": str(exc)}
        payment_id = self._repo.record_payment(user_id, amount, method)
        AuditService().log_event("record_payment", user_id, {"amount": amount, "method": method})
        NotificationService().create_notification(user_id, "payment_recorded", f"Payment of {amount} via {method} received.")
        result = {"status": "Payment recorded", "payment_id": payment_id}
        store_idempotency_result(idempotency_key, "/billing/record_payment", user_id, result)
        return result

    def get_payment_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Return the user's full payment history."""
        return self._repo.get_payment_history(user_id)

    def generate_billing_metrics(self, user_id: str) -> Dict[str, Any]:
        """Return total paid and subscription count for the user."""
        return self._repo.generate_billing_metrics(user_id)
