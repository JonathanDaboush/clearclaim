# NotificationController handler function
def handle_send_notification(user_id: str, event_type: str, content: str, related_object_id: str, related_object_type: str) -> dict:
    """
    Handler for sending notification.
    Args: user_id, event_type, content, related_object_id, related_object_type. Returns: dict result.
    """
    pass
from services.notification_service import NotificationService

notification_service = NotificationService()

def create_notification(user_id, event_type, content):
    """Controller for creating notification."""
    return notification_service.create_notification(user_id, event_type, content)

def resolve_notification_recipients(event_type, project_id):
    """Controller for resolving notification recipients."""
    return notification_service.resolve_notification_recipients(event_type, project_id)

def send_email_notification(user_id, subject, message):
    """Controller for sending email notification."""
    return notification_service.send_email_notification(user_id, subject, message)

def send_in_app_notification(user_id, message):
    """Controller for sending in-app notification."""
    return notification_service.send_in_app_notification(user_id, message)

def mark_notification_read(notification_id):
    """Controller for marking notification read."""
    return notification_service.mark_notification_read(notification_id)

def get_user_notifications(user_id):
    """Controller for getting user notifications."""
    return notification_service.get_user_notifications(user_id)
