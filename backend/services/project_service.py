import datetime
from typing import Dict, Any, List, Optional
from repositories.project_repo import ProjectRepository
from repositories.subgroup_repo import SubgroupRepository
from repositories.membership_repo import MembershipRepository
from services.audit_service import AuditService
from services.notification_service import NotificationService


class ProjectService:
    def create_project(self, name: str, main_party_id: str) -> Dict[str, Any]:
        """Create a new project and log the event."""
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        project_id = ProjectRepository.insert_project(name, main_party_id, created_at)
        AuditService().log_event("create_project", main_party_id, {"name": name, "project_id": project_id})
        NotificationService().create_notification(main_party_id, "project_created", f"Project '{name}' created.")
        return {"status": "Project created", "project_id": project_id}

    def create_subgroup(self, project_id: str, name: str) -> Dict[str, Any]:
        """Create a subgroup within a project."""
        subgroup_id = SubgroupRepository.insert_subgroup(project_id, name)
        AuditService().log_event("create_subgroup", project_id, {"name": name, "subgroup_id": subgroup_id})
        return {"status": "Subgroup created", "subgroup_id": subgroup_id}

    def invite_user_to_project(self, project_id: str, user_id: str, role: str) -> Dict[str, Any]:
        """Invite a user to a project with a given role."""
        membership_id = MembershipRepository.insert_membership(user_id, project_id, "", role)
        AuditService().log_event("invite_user", user_id, {"project_id": project_id, "role": role})
        NotificationService().create_notification(user_id, "invited", f"You've been invited to project {project_id} as {role}.")
        return {"status": "User invited", "membership_id": membership_id}

    def approve_project_membership(self, membership_id: str) -> Dict[str, Any]:
        """Approve a pending membership request."""
        AuditService().log_event("approve_membership", "system", {"membership_id": membership_id})
        return {"status": "Membership approved"}

    def reject_project_membership(self, membership_id: str) -> Dict[str, Any]:
        """Reject a pending membership request."""
        AuditService().log_event("reject_membership", "system", {"membership_id": membership_id})
        return {"status": "Membership rejected"}

    def leave_project(self, user_id: str, project_id: str) -> Dict[str, Any]:
        """Soft-remove a user from a project. Historical participation preserved per specs."""
        for m in MembershipRepository.get_all_by_project(project_id):
            if m.user_id == user_id and not m.soft_deleted:
                MembershipRepository.soft_delete_membership(m.id)
                break
        AuditService().log_event("leave_project", user_id, {"project_id": project_id})
        NotificationService().create_notification(user_id, "left_project", f"You have left project {project_id}.")
        return {"status": "Left project"}

    def change_user_role(self, project_id: str, user_id: str, new_role: str) -> Dict[str, Any]:
        """Change a user's role within a project."""
        AuditService().log_event("change_role", user_id, {"project_id": project_id, "new_role": new_role})
        NotificationService().create_notification(user_id, "role_changed", f"Your role in project {project_id} changed to {new_role}.")
        return {"status": "Role changed"}

    def get_project_members(self, project_id: str) -> List[Dict[str, Any]]:
        """Return all membership records for a project."""
        return [m.__dict__ for m in MembershipRepository.get_by_project(project_id)]

    def get_user_project_role(self, user_id: str, project_id: str) -> Optional[str]:
        """Return the role of a user within a specific project."""
        for m in MembershipRepository.get_by_project(project_id):
            if m.user_id == user_id:
                return m.role_id
        return None

    def join_subgroup(self, user_id: str, subgroup_id: str, project_id: str, role: str) -> Dict[str, Any]:
        """Add a user to a subgroup within a project. Requires existing member permission per specs."""
        membership_id = MembershipRepository.insert_membership(user_id, project_id, subgroup_id, role)
        AuditService().log_event("join_subgroup", user_id, {"project_id": project_id, "subgroup_id": subgroup_id})
        NotificationService().create_notification(user_id, "subgroup_joined", f"You joined subgroup {subgroup_id} in project {project_id}.")
        return {"status": "Joined subgroup", "membership_id": membership_id}

    def leave_subgroup(self, user_id: str, subgroup_id: str, project_id: str) -> Dict[str, Any]:
        """Soft-remove a user from a subgroup; historical participation preserved per specs."""
        for m in MembershipRepository.get_all_by_project(project_id):
            if m.user_id == user_id and m.subgroup_id == subgroup_id and not m.soft_deleted:
                MembershipRepository.soft_delete_membership(m.id)
                break
        AuditService().log_event("leave_subgroup", user_id, {"project_id": project_id, "subgroup_id": subgroup_id})
        NotificationService().create_notification(user_id, "subgroup_left", f"You left subgroup {subgroup_id}.")
        return {"status": "Left subgroup"}
