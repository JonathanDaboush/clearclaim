# BillingController calls BillingService
from services.billing_service import BillingService

billing_service = BillingService()

def create_subscription(user_id, tier):
    """Controller for creating subscription."""
    return billing_service.create_subscription(user_id, tier)

def cancel_subscription(user_id):
    """Controller for cancelling subscription."""
    return billing_service.cancel_subscription(user_id)

def update_subscription_status(user_id, status):
    """Controller for updating subscription status."""
    return billing_service.update_subscription_status(user_id, status)

def record_payment(user_id, amount, method):
    """Controller for recording payment."""
    return billing_service.record_payment(user_id, amount, method)

def get_payment_history(user_id):
    """Controller for getting payment history."""
    return billing_service.get_payment_history(user_id)

def generate_billing_metrics(user_id):
    """Controller for generating billing metrics."""
    return billing_service.generate_billing_metrics(user_id)
