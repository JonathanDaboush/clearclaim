# NotificationController handler function
from typing import Dict, Any, List
from services.notification_service import NotificationService

notification_service = NotificationService()


def handle_send_notification(user_id: str, event_type: str, content: str, related_object_id: str, related_object_type: str) -> Dict[str, Any]:
    """Send a notification, route to email for breach/consent/accessibility events."""
    return notification_service.create_notification(user_id, event_type, content)


def create_notification(user_id: str, event_type: str, content: str) -> Dict[str, Any]:
    """Controller for creating notification."""
    return notification_service.create_notification(user_id, event_type, content)

def resolve_notification_recipients(event_type: str, project_id: str) -> List[str]:
    """Controller for resolving notification recipients."""
    return notification_service.resolve_notification_recipients(event_type, project_id)

def send_email_notification(user_id: str, subject: str, message: str) -> None:
    """Controller for sending email notification."""
    notification_service.send_email_notification(user_id, subject, message)

def send_in_app_notification(user_id: str, message: str) -> None:
    """Controller for sending in-app notification."""
    notification_service.send_in_app_notification(user_id, message)

def mark_notification_read(notification_id: str) -> bool:
    """Controller for marking notification read."""
    return notification_service.mark_notification_read(notification_id)

def get_user_notifications(user_id: str) -> List[Dict[str, Any]]:
    """Controller for getting user notifications."""
    return notification_service.get_user_notifications(user_id)
