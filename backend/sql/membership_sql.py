import uuid


class MembershipSQL:
    def insert_membership(self, user_id: str, project_id: str, subgroup_id: str, role_id: str) -> str:
        """Return the SQL insert values for a membership record. Returns new membership ID."""
        return str(uuid.uuid4())  # In production: delegate to SQLTemplate.insert(...)

    def delete_membership(self, membership_id: str) -> bool:
        """Return True after SQL DELETE for membership record."""
        return True  # In production: delegate to SQLTemplate.delete(...)
