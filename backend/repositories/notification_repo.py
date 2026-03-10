import uuid
import datetime
from typing import List, Optional
from models.notification_model import Notification


class NotificationRepository:
    _notifications: List[Notification] = []  # In-memory (replace with DB in production)

    @staticmethod
    def insert_notification(user_id: str, event_type: str, content: str, related_object_id: str, related_object_type: str, sent_at: str) -> str:
        """Store a notification record. Returns the new notification ID."""
        notification_id = str(uuid.uuid4())
        NotificationRepository._notifications.append(Notification(
            id=notification_id,
            user_id=user_id,
            event_type=event_type,
            content=content,
            related_object_id=related_object_id,
            related_object_type=related_object_type,
            sent_at=sent_at,
        ))
        return notification_id

    @staticmethod
    def mark_read(notification_id: str) -> bool:
        """Mark a notification as read by setting read_at to the current UTC time. Returns True if found."""
        for n in NotificationRepository._notifications:
            if n.id == notification_id and n.read_at is None:
                n.read_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
                return True
        return False

    @staticmethod
    def delete_notification(notification_id: str) -> bool:
        """Remove a notification record. Returns True if found."""
        for n in NotificationRepository._notifications:
            if n.id == notification_id:
                NotificationRepository._notifications.remove(n)
                return True
        return False

    @staticmethod
    def get_by_user(user_id: str) -> List[Notification]:
        """Return all notification records for a given user."""
        return [n for n in NotificationRepository._notifications if n.user_id == user_id]
