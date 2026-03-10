from typing import Dict, Set

# Contract states
DRAFT = "draft"
REVISION_PENDING = "revision_pending"
REVISION_APPROVED = "revision_approved"
READY_FOR_SIGNATURE = "ready_for_signature"
FULLY_SIGNED = "fully_signed"
ARCHIVED = "archived"

VALID_TRANSITIONS: Dict[str, Set[str]] = {
    DRAFT: {REVISION_PENDING, READY_FOR_SIGNATURE},
    REVISION_PENDING: {REVISION_APPROVED, DRAFT},
    REVISION_APPROVED: {READY_FOR_SIGNATURE},
    READY_FOR_SIGNATURE: {FULLY_SIGNED},
    FULLY_SIGNED: {ARCHIVED},
    ARCHIVED: set(),
}

_contract_states: Dict[str, str] = {}  # contract_id -> state (replace with DB in production)


def get_contract_state(contract_id: str) -> str:
    """Return the current state of a contract, defaulting to DRAFT."""
    return _contract_states.get(contract_id, DRAFT)


def validate_state_transition(current_state: str, new_state: str) -> bool:
    """Return True if transitioning from current_state to new_state is allowed."""
    return new_state in VALID_TRANSITIONS.get(current_state, set())


def transition_contract_state(contract_id: str, new_state: str) -> bool:
    """Transition a contract to a new state if the transition is valid. Returns True on success."""
    current = get_contract_state(contract_id)
    if not validate_state_transition(current, new_state):
        raise ValueError(f"Invalid transition: {current} -> {new_state}")
    _contract_states[contract_id] = new_state
    return True
