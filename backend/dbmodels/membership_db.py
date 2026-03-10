from typing import Optional

# MembershipDB for persistence mapping
class MembershipDB:
    def __init__(self, id: str, user_id: str, project_id: str, subgroup_id: str, role_id: str, left_at: Optional[str] = None, soft_deleted: bool = False):
        """
        Persistence model for DB operations.
        Args:
            id (str): Membership ID
            user_id (str): User ID
            project_id (str): Project ID
            subgroup_id (str): Subgroup ID
            role_id (str): Role ID
            left_at (str): UTC timestamp when user left, or None
            soft_deleted (bool): Whether this membership has been soft-deleted
        """
        self.id = id
        self.user_id = user_id
        self.project_id = project_id
        self.subgroup_id = subgroup_id
        self.role_id = role_id
        self.left_at = left_at
        self.soft_deleted = soft_deleted
