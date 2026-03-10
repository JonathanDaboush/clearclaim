import uuid
import datetime
from typing import List
from models.membership_model import Membership


class MembershipRepository:
    _memberships: List[Membership] = []  # In-memory (replace with DB in production)

    @staticmethod
    def insert_membership(user_id: str, project_id: str, subgroup_id: str, role_id: str) -> str:
        """Add a user to a project/subgroup with a role. Returns the new membership ID."""
        membership_id = str(uuid.uuid4())
        MembershipRepository._memberships.append(Membership(
            id=membership_id,
            user_id=user_id,
            project_id=project_id,
            subgroup_id=subgroup_id,
            role_id=role_id,
        ))
        return membership_id

    @staticmethod
    def soft_delete_membership(membership_id: str) -> bool:
        """Soft-delete a membership by setting left_at and soft_deleted=True.
        Historical participation is preserved per specs."""
        for m in MembershipRepository._memberships:
            if m.id == membership_id and not m.soft_deleted:
                m.soft_deleted = True
                m.left_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
                return True
        return False

    @staticmethod
    def delete_membership(membership_id: str) -> bool:
        """Hard-remove a membership record. Use soft_delete_membership for leaving users."""
        for m in MembershipRepository._memberships:
            if m.id == membership_id:
                MembershipRepository._memberships.remove(m)
                return True
        return False

    @staticmethod
    def get_by_project(project_id: str) -> List[Membership]:
        """Return all active (non-soft-deleted) memberships for a given project."""
        return [m for m in MembershipRepository._memberships if m.project_id == project_id and not m.soft_deleted]

    @staticmethod
    def get_all_by_project(project_id: str) -> List[Membership]:
        """Return all memberships (including left users) for a project, for audit purposes."""
        return [m for m in MembershipRepository._memberships if m.project_id == project_id]
