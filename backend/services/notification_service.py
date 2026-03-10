# NotificationService handles email and in-app notifications
class NotificationService:
    def create_notification(self, user_id, event_type, content):
        """Create notification for user."""
        pass

    def resolve_notification_recipients(self, event_type, project_id):
        """Resolve recipients for notification event."""
        pass

    def send_email_notification(self, user_id, subject, message):
        """Send email notification to user."""
        pass

    def send_in_app_notification(self, user_id, message):
        """Send in-app notification to user."""
        pass

    def mark_notification_read(self, notification_id):
        """Mark notification as read."""
        pass

    def get_user_notifications(self, user_id):
        """Get all notifications for user."""
        pass
