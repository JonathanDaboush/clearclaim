import datetime
from typing import List, Dict, Any
from repositories.notification_repo import NotificationRepository


class NotificationService:
    def create_notification(self, user_id: str, event_type: str, content: str) -> Dict[str, Any]:
        """Create and store a notification. Routes breach/consent events to email."""
        sent_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        notification_id = NotificationRepository.insert_notification(
            user_id=user_id,
            event_type=event_type,
            content=content,
            related_object_id="",
            related_object_type="",
            sent_at=sent_at,
        )
        if event_type == "breach":
            self.send_email_notification(user_id, "Security Alert", content)
        elif event_type == "parental_consent":
            self.send_email_notification(user_id, "Parental Consent Required", content)
        elif event_type in ("consent", "accessibility"):
            self.send_email_notification(user_id, event_type.replace("_", " ").title(), content)
        else:
            self.send_in_app_notification(user_id, content)
        return {"status": "Notification created", "notification_id": notification_id}

    def resolve_notification_recipients(self, event_type: str, project_id: str) -> List[str]:
        """Return the list of user IDs that should receive a notification for this event."""
        from utils.notification_recipient_resolver import NotificationRecipientResolver
        return NotificationRecipientResolver.resolve_recipients(project_id, event_type)

    def send_email_notification(self, user_id: str, subject: str, message: str):
        """Send an email notification (handed off to async task)."""
        from services.async_tasks import AsyncTasks
        AsyncTasks.send_email_async(user_id, subject, message)

    def send_in_app_notification(self, user_id: str, message: str):
        """Persist an in-app notification (already stored in repository above)."""
        pass  # Already persisted via NotificationRepository.insert_notification

    def mark_notification_read(self, notification_id: str) -> bool:
        """Mark a notification as read by setting read_at."""
        return NotificationRepository.mark_read(notification_id)

    def get_user_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Return all notifications for a user."""
        return [vars(n) for n in NotificationRepository.get_by_user(user_id)]
