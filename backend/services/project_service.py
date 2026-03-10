# ProjectService handles project, subgroup, membership, and permission logic
class ProjectService:
    def create_project(self, name, main_party_id):
        """Create new project."""
        pass

    def create_subgroup(self, project_id, name):
        """Create subgroup container."""
        pass

    def invite_user_to_project(self, project_id, user_id, role):
        """Invite user to project with role."""
        pass

    def approve_project_membership(self, request_id):
        """Approve project membership request."""
        pass

    def reject_project_membership(self, request_id):
        """Reject project membership request."""
        pass

    def leave_project(self, user_id, project_id):
        """User leaves project."""
        pass

    def change_user_role(self, project_id, user_id, new_role):
        """Change user's role in project."""
        pass

    def get_project_members(self, project_id):
        """Get all members of project."""
        pass

    def get_user_project_role(self, user_id, project_id):
        """Get user's role in project."""
        pass
