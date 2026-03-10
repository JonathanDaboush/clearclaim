# BillingRepository handles subscription and payment persistence
class BillingRepository:
    def create_subscription(self, user_id, tier):
        """Create subscription record."""
        pass

    def cancel_subscription(self, user_id):
        """Cancel subscription for user."""
        pass

    def update_subscription_status(self, user_id, status):
        """Update subscription status for user."""
        pass

    def record_payment(self, user_id, amount, method):
        """Record payment for user."""
        pass

    def get_payment_history(self, user_id):
        """Get payment history for user."""
        pass

    def generate_billing_metrics(self, user_id):
        """Generate billing metrics for user."""
        pass
