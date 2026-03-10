import uuid
from typing import Optional


class Project:
    def __init__(self, id: str, name: str, main_party_id: str, created_at: str, deleted_at: Optional[str] = None):
        """
        Project entity.
        Args:
            id (str): Project ID
            name (str): Project name
            main_party_id (str): Main party user ID
            created_at (str): UTC timestamp
            deleted_at (str): UTC timestamp or None
        """
        self.id = id
        self.name = name
        self.main_party_id = main_party_id
        self.created_at = created_at
        self.deleted_at = deleted_at

    def validate_project_name(self, name: str) -> bool:
        """
        Validate project name.
        Returns True if valid, else False.
        """
        return bool(name and len(name) > 2)

    def generate_project_id(self) -> str:
        """
        Generate unique project ID.
        Returns a UUID.
        """
        return str(uuid.uuid4())
