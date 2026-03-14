"""Centralized permission policy engine.

Every authorization decision in the application goes through this module.
No controller or service should repeat inline role checks — call
`Policy.enforce()` or `Policy.can()` instead.

Usage:
    from utils.policy import Policy

    # Raises PermissionDenied if not allowed (use in service layer)
    Policy.enforce(user_id, "sign_contract", project_id=project_id)

    # Returns bool (use in conditional logic)
    if Policy.can(user_id, "delete_evidence", project_id=project_id):
        ...

    # Resource ownership check — user must own OR have the permission
    Policy.enforce_ownership_or_permission(
        user_id, resource_owner_id, "delete_evidence", project_id=project_id
    )
"""
from __future__ import annotations

from typing import Optional
from repositories.membership_repo import MembershipRepository


# ── Permission table ──────────────────────────────────────────────────────────
# Single source of truth; mirrors the role table seeded in db._seed_roles()

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "worker_manager": {
        "create_contract",
        "revise_contract",
        "approve_revision",
        "reject_revision",
        "add_evidence",
        "delete_evidence",
        "sign_contract",
        "manage_workers",
        "view",
    },
    "worker": {
        "create_contract",
        "revise_contract",
        "approve_revision",
        "add_evidence",
        "sign_contract",
        "view",
    },
    "legal_rep": {
        "approve_revision",
        "reject_revision",
        "add_evidence",
        "sign_contract",
        "view",
    },
    "client": {
        "sign_contract",
        "view",
    },
    "guest": {
        "view",
    },
}


class PermissionDenied(Exception):
    """Raised by Policy.enforce() when the user lacks the required permission."""

    def __init__(self, user_id: str, action: str, project_id: str):
        self.user_id = user_id
        self.action = action
        self.project_id = project_id
        super().__init__(
            f"User {user_id!r} is not allowed to perform {action!r} "
            f"in project {project_id!r}."
        )


class Policy:
    """Stateless policy engine — all methods are classmethods."""

    @classmethod
    def _get_role(cls, user_id: str, project_id: str) -> str:
        for m in MembershipRepository.get_by_project(project_id):
            if m.user_id == user_id:
                return m.role_id or "guest"
        return "guest"

    @classmethod
    def can(
        cls,
        user_id: str,
        action: str,
        project_id: str,
    ) -> bool:
        """Return True if user has permission to perform *action* in *project*."""
        role = cls._get_role(user_id, project_id)
        return action in ROLE_PERMISSIONS.get(role, set())

    @classmethod
    def enforce(
        cls,
        user_id: str,
        action: str,
        project_id: str,
    ) -> None:
        """Raise PermissionDenied if user cannot perform *action* in *project*.

        Preferred over `can()` in service layer — forces callers to handle the
        error explicitly, avoiding silent permission bypasses.
        """
        if not cls.can(user_id, action, project_id):
            raise PermissionDenied(user_id, action, project_id)

    @classmethod
    def enforce_ownership_or_permission(
        cls,
        user_id: str,
        resource_owner_id: str,
        action: str,
        project_id: str,
    ) -> None:
        """Allow if user owns the resource OR has the permission via their role.

        Useful for "user can always manage their own resource" patterns.
        """
        if user_id == resource_owner_id:
            return  # owner always allowed
        cls.enforce(user_id, action, project_id)

    @classmethod
    def get_role(cls, user_id: str, project_id: str) -> str:
        """Return the user's role string in a project (public accessor)."""
        return cls._get_role(user_id, project_id)
