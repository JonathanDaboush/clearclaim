# NotificationRepository for PostgreSQL
class NotificationRepository:
    @staticmethod
    def insert_notification(user_id: str, event_type: str, content: str, related_object_id: str, related_object_type: str, sent_at: str):
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

    @staticmethod
    def delete_notification(notification_id: str):
        """
        Delete notification record.
        Args:
            notification_id (str): Notification ID
        Returns:
            bool: Success
        """
        pass
