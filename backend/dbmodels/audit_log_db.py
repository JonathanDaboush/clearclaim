# AuditLogDB for persistence mapping
class AuditLogDB:
    def __init__(self, id: str, user_id: str, device_id: str, event_type: str, related_object_id: str, details: str, timestamp: str, hash: str):
        """
        Persistence model for DB operations.
        Args:
            id (str): Log ID
            user_id (str): User ID
            device_id (str): Device ID
            event_type (str): Event type
            related_object_id (str): Related object ID
            details (str): Event details
            timestamp (str): UTC timestamp
            hash (str): Cryptographic hash
        """
        self.id = id
        self.user_id = user_id
        self.device_id = device_id
        self.event_type = event_type
        self.related_object_id = related_object_id
        self.details = details
        self.timestamp = timestamp
        self.hash = hash
