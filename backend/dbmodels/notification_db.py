from typing import Optional

# NotificationDB for persistence mapping
class NotificationDB:
    def __init__(self, id: str, user_id: str, event_type: str, content: str, related_object_id: str, related_object_type: str, sent_at: str, read_at: Optional[str] = None):
        """
        Persistence model for DB operations.
        Args:
            id (str): Notification ID
            user_id (str): User ID
            event_type (str): Event type
            content (str): Notification content
            related_object_id (str): Related object ID
            related_object_type (str): Related object type
            sent_at (str): UTC timestamp
            read_at (str): UTC timestamp when read, or None
        """
        self.id = id
        self.user_id = user_id
        self.event_type = event_type
        self.content = content
        self.related_object_id = related_object_id
        self.related_object_type = related_object_type
        self.sent_at = sent_at
        self.read_at = read_at
