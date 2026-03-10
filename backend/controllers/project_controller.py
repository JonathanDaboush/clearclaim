# ProjectController handler functions
    """
    Handler for creating project.
    Args: name, main_party_id. Returns: dict result.
    """
    pass

    """
    Handler for creating subgroup.
    Args: project_id, name. Returns: dict result.
    """
    pass

    """
    Handler for adding member.
    Args: user_id, project_id, subgroup_id, role_id. Returns: dict result.
    """
    pass

    """
    Handler for removing member.
    Args: user_id, project_id, subgroup_id. Returns: dict result.
    """
    pass
# ProjectController calls ProjectService
from services.project_service import ProjectService

project_service = ProjectService()

def create_project(name, main_party_id):
    """Controller for creating project."""
    return project_service.create_project(name, main_party_id)

def create_subgroup(project_id, name):
    """Controller for creating subgroup."""
    return project_service.create_subgroup(project_id, name)

def invite_user_to_project(project_id, user_id, role):
    """Controller for inviting user to project."""
    return project_service.invite_user_to_project(project_id, user_id, role)

def approve_project_membership(request_id):
    """Controller for approving project membership."""
    return project_service.approve_project_membership(request_id)

def reject_project_membership(request_id):
    """Controller for rejecting project membership."""
    return project_service.reject_project_membership(request_id)

def leave_project(user_id, project_id):
    """Controller for leaving project."""
    return project_service.leave_project(user_id, project_id)

def change_user_role(project_id, user_id, new_role):
    """Controller for changing user role."""
    return project_service.change_user_role(project_id, user_id, new_role)

def get_project_members(project_id):
    """Controller for getting project members."""
    return project_service.get_project_members(project_id)

def get_user_project_role(user_id, project_id):
    """Controller for getting user project role."""
    return project_service.get_user_project_role(user_id, project_id)
