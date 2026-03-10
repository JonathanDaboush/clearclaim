from typing import List
from models.membership_model import Membership
from repositories.membership_repo import MembershipRepository


class NotificationRecipientResolver:
    @staticmethod
    def resolve_recipients(project_id: str, event_type: str) -> List[str]:
        """Return user IDs of all active members of a project who should receive a notification.
        For breach events, returns all members. For role-specific events, filter by role."""
        members: List[Membership] = MembershipRepository.get_by_project(project_id)
        if event_type == "breach":
            return [m.user_id for m in members]
        role_map = {
            "revision_created": {"worker_manager", "worker", "legal_rep"},
            "revision_approved": {"worker_manager", "worker", "legal_rep"},
            "signature_request": {"worker_manager", "worker", "legal_rep", "client"},
            "evidence_uploaded": {"worker_manager", "worker", "legal_rep"},
            "evidence_proposed": {"worker_manager", "worker", "legal_rep"},
        }
        allowed_roles = role_map.get(event_type, {m.role_id for m in members})
        return [m.user_id for m in members if m.role_id in allowed_roles]
