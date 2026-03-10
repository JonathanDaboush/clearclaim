# NotificationSQL class for notification DB operations
class NotificationSQL:
    def insert_notification(self, user_id: str, event_type: str, content: str, related_object_id: str, related_object_type: str, sent_at: str) -> str:
        """
        Insert notification record.
        Args:
            user_id (str): User ID
            event_type (str): Event type
            content (str): Notification content
            related_object_id (str): Related object ID
            related_object_type (str): Related object type
            sent_at (str): UTC timestamp
        Returns:
            str: Notification ID
        """
        pass
