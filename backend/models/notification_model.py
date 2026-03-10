# Notification model
class Notification:
    def __init__(self, id, user_id, event_type, content, related_object_id, related_object_type, sent_at):
        """
        Notification entity.
        Args:
            id (str): Notification ID
            user_id (str): User ID
            event_type (str): Event type
            content (str): Notification content
            related_object_id (str): Related object ID
            related_object_type (str): Related object type
            sent_at (str): UTC timestamp
        """
        self.id = id
        self.user_id = user_id
        self.event_type = event_type
        self.content = content
        self.related_object_id = related_object_id
        self.related_object_type = related_object_type
        self.sent_at = sent_at
