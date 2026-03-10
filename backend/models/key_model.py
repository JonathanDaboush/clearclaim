from typing import Optional

# Key types per hierarchy spec: root (offline/HSM), system (HSM), session (ephemeral per device)
KEY_TYPE_ROOT = "root"
KEY_TYPE_SYSTEM = "system"
KEY_TYPE_SESSION = "session"

# Key statuses
KEY_STATUS_ACTIVE = "active"
KEY_STATUS_ROTATED = "rotated"
KEY_STATUS_REVOKED = "revoked"


class Key:
    def __init__(self, id: str, type: str, created_at: str, parent_id: Optional[str] = None, rotated_at: Optional[str] = None, status: str = KEY_STATUS_ACTIVE):
        """
        Key entity representing the hierarchical key system.
        Args:
            id (str): Key ID
            type (str): Key type — root, system, or session
            created_at (str): UTC timestamp of creation
            parent_id (str): ID of the parent key (None for root)
            rotated_at (str): UTC timestamp when rotated, or None
            status (str): Key status — active, rotated, or revoked
        """
        self.id = id
        self.type = type
        self.created_at = created_at
        self.parent_id = parent_id
        self.rotated_at = rotated_at
        self.status = status
