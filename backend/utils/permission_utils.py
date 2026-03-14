"""Thin compatibility shim — delegates all permission checks to utils.policy.Policy.

Existing call sites (e.g. contract_controller.py) continue to work unchanged.
New code should import Policy directly for fine-grained control.
"""
from utils.policy import Policy, ROLE_PERMISSIONS   # re-export for callers that import from here

# ── Backwards-compatible helpers ──────────────────────────────────────────────

def check_permission(user_id: str, action: str, project_id: str) -> bool:
    return Policy.can(user_id, action, project_id)


def can_sign_contract(user_id: str, project_id: str) -> bool:
    return Policy.can(user_id, "sign_contract", project_id)


def can_add_evidence(user_id: str, project_id: str) -> bool:
    return Policy.can(user_id, "add_evidence", project_id)


def can_delete_evidence(user_id: str, project_id: str) -> bool:
    return Policy.can(user_id, "delete_evidence", project_id)


def can_revise_contract(user_id: str, project_id: str) -> bool:
    return Policy.can(user_id, "revise_contract", project_id)


def can_approve_revision(user_id: str, project_id: str) -> bool:
    return Policy.can(user_id, "approve_revision", project_id)


def can_manage_workers(user_id: str, project_id: str) -> bool:
    return Policy.can(user_id, "manage_workers", project_id)
