# ProjectController calls ProjectService
from typing import Dict, Any, List, Optional
from services.project_service import ProjectService

project_service = ProjectService()

def create_project(name: str, main_party_id: str) -> Dict[str, Any]:
    """Controller for creating project."""
    return project_service.create_project(name, main_party_id)

def create_subgroup(project_id: str, name: str) -> Dict[str, Any]:
    """Controller for creating subgroup."""
    return project_service.create_subgroup(project_id, name)

def invite_user_to_project(project_id: str, user_id: str, role: str) -> Dict[str, Any]:
    """Controller for inviting user to project."""
    return project_service.invite_user_to_project(project_id, user_id, role)

def approve_project_membership(request_id: str) -> Dict[str, Any]:
    """Controller for approving project membership."""
    return project_service.approve_project_membership(request_id)

def reject_project_membership(request_id: str) -> Dict[str, Any]:
    """Controller for rejecting project membership."""
    return project_service.reject_project_membership(request_id)

def leave_project(user_id: str, project_id: str) -> Dict[str, Any]:
    """Controller for leaving project."""
    return project_service.leave_project(user_id, project_id)

def change_user_role(project_id: str, user_id: str, new_role: str) -> Dict[str, Any]:
    """Controller for changing user role."""
    return project_service.change_user_role(project_id, user_id, new_role)

def get_project_members(project_id: str) -> List[Dict[str, Any]]:
    """Controller for getting project members."""
    return project_service.get_project_members(project_id)

def get_user_project_role(user_id: str, project_id: str) -> Optional[str]:
    """Controller for getting user project role."""
    return project_service.get_user_project_role(user_id, project_id)

def join_subgroup(user_id: str, subgroup_id: str, project_id: str, role: str) -> Dict[str, Any]:
    """Controller for joining a subgroup within a project."""
    return project_service.join_subgroup(user_id, subgroup_id, project_id, role)

def leave_subgroup(user_id: str, subgroup_id: str, project_id: str) -> Dict[str, Any]:
    """Controller for leaving a subgroup within a project."""
    return project_service.leave_subgroup(user_id, subgroup_id, project_id)
