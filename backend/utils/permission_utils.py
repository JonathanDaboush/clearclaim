from repositories.membership_repo import MembershipRepository

ROLE_PERMISSIONS = {
    "worker_manager": {"sign_contract", "add_evidence", "delete_evidence", "revise_contract", "approve_revision", "manage_workers", "view"},
    "worker":         {"sign_contract", "add_evidence", "revise_contract", "approve_revision", "view"},
    "legal_rep":      {"sign_contract", "approve_revision", "add_evidence", "view"},
    "client":         {"sign_contract", "view"},
    "guest":          {"view"},
}


def _get_role(user_id: str, project_id: str) -> str:
    for m in MembershipRepository.get_by_project(project_id):
        if m.user_id == user_id:
            return m.role_id or "guest"
    return "guest"


def check_permission(user_id: str, action: str, project_id: str) -> bool:
    """Return True if the user has permission to perform action in the project."""
    role = _get_role(user_id, project_id)
    return action in ROLE_PERMISSIONS.get(role, set())


def can_sign_contract(user_id: str, project_id: str) -> bool:
    """Return True if the user's role allows signing contracts."""
    return check_permission(user_id, "sign_contract", project_id)


def can_add_evidence(user_id: str, project_id: str) -> bool:
    """Return True if the user's role allows adding evidence."""
    return check_permission(user_id, "add_evidence", project_id)


def can_delete_evidence(user_id: str, project_id: str) -> bool:
    """Return True if the user's role allows deleting evidence."""
    return check_permission(user_id, "delete_evidence", project_id)


def can_revise_contract(user_id: str, project_id: str) -> bool:
    """Return True if the user's role allows revising contracts."""
    return check_permission(user_id, "revise_contract", project_id)


def can_approve_revision(user_id: str, project_id: str) -> bool:
    """Return True if the user's role allows approving revisions."""
    return check_permission(user_id, "approve_revision", project_id)


def can_manage_workers(user_id: str, project_id: str) -> bool:
    """Return True if the user's role allows managing (inviting/changing) other workers.
    Only worker_manager has this permission."""
    return check_permission(user_id, "manage_workers", project_id)
