# PaymentController calls BillingService
from typing import Dict, Any, List
from services.billing_service import BillingService

billing_service = BillingService()

def create_subscription(user_id: str, tier: str) -> Dict[str, Any]:
    """Controller for creating subscription."""
    return billing_service.create_subscription(user_id, tier)

def cancel_subscription(user_id: str) -> Dict[str, Any]:
    """Controller for cancelling subscription."""
    return billing_service.cancel_subscription(user_id)

def update_subscription_status(user_id: str, status: str) -> Dict[str, Any]:
    """Controller for updating subscription status."""
    return billing_service.update_subscription_status(user_id, status)

def record_payment(user_id: str, amount: float, method: str) -> Dict[str, Any]:
    """Controller for recording payment."""
    return billing_service.record_payment(user_id, amount, method)

def get_payment_history(user_id: str) -> List[Dict[str, Any]]:
    """Controller for getting payment history."""
    return billing_service.get_payment_history(user_id)

def generate_billing_metrics(user_id: str) -> Dict[str, Any]:
    """Controller for generating billing metrics."""
    return billing_service.generate_billing_metrics(user_id)
