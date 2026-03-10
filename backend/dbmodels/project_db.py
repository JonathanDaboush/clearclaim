from typing import Optional


# ProjectDB for persistence mapping
class ProjectDB:
    def __init__(self, id: str, name: str, main_party_id: str, created_at: str, deleted_at: Optional[str]):
        """
        Persistence model for DB operations.
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
