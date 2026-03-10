import uuid


class NotificationSQL:
    def insert_notification(self, user_id: str, event_type: str, content: str, related_object_id: str, related_object_type: str, sent_at: str) -> str:
        """Return the SQL insert values for a notification record. Returns new notification ID."""
        return str(uuid.uuid4())  # In production: delegate to SQLTemplate.insert(...)
