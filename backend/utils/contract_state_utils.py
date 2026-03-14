import datetime
from typing import Dict, Set
import db as _db

# ── Contract states ───────────────────────────────────────────────────────────
DRAFT                = "draft"               # initial; revisions allowed
PROPOSED             = "proposed"            # submitted for party review
REVISION_PENDING     = "revision_pending"    # revision changes under review
REVISION_APPROVED    = "revision_approved"   # all parties approved revision
READY_FOR_SIGNATURE  = "ready_for_signature" # locked for signing
FULLY_SIGNED         = "fully_signed"        # all required parties signed
REJECTED             = "rejected"            # explicitly rejected — terminal
ARCHIVED             = "archived"            # closed — terminal

# ── Legal state machine ───────────────────────────────────────────────────────
# Only the transitions listed here are permitted; all others raise ValueError.
VALID_TRANSITIONS: Dict[str, Set[str]] = {
    DRAFT:               {PROPOSED, REJECTED, REVISION_PENDING, READY_FOR_SIGNATURE},
    PROPOSED:            {REVISION_PENDING, READY_FOR_SIGNATURE, REJECTED},
    REVISION_PENDING:    {REVISION_APPROVED, READY_FOR_SIGNATURE, REJECTED, DRAFT},
    REVISION_APPROVED:   {READY_FOR_SIGNATURE},
    READY_FOR_SIGNATURE: {FULLY_SIGNED, REJECTED},
    FULLY_SIGNED:        {ARCHIVED},
    REJECTED:            set(),   # terminal
    ARCHIVED:            set(),   # terminal
}

# States in which content edits are forbidden (contract is legally locked)
LOCKED_STATES: Set[str] = {READY_FOR_SIGNATURE, FULLY_SIGNED, REJECTED, ARCHIVED}


def get_contract_state(contract_id: str) -> str:
    """Return the current state of a contract persisted in the contracts table."""
    rows = _db.query(
        "SELECT status FROM contracts WHERE id = %s",
        (contract_id,),
    )
    if not rows:
        return DRAFT
    return rows[0]["status"] or DRAFT


def validate_state_transition(current_state: str, new_state: str) -> bool:
    """Return True if transitioning from current_state to new_state is permitted."""
    return new_state in VALID_TRANSITIONS.get(current_state, set())


def transition_contract_state(contract_id: str, new_state: str) -> bool:
    """Atomically transition a contract to new_state in the DB.

    Raises ValueError for illegal transitions so callers get a clear error
    rather than silently ignoring the request.
    """
    current = get_contract_state(contract_id)
    if not validate_state_transition(current, new_state):
        raise ValueError(
            f"Illegal contract state transition: {current!r} → {new_state!r}. "
            f"Allowed next states from {current!r}: {sorted(VALID_TRANSITIONS.get(current, set()))}"
        )
    _db.execute(
        "UPDATE contracts SET status = %s WHERE id = %s",
        (new_state, contract_id),
    )
    return True


def assert_contract_editable(contract_id: str) -> None:
    """Raise ValueError if the contract is in a state that forbids content changes."""
    state = get_contract_state(contract_id)
    if state in LOCKED_STATES:
        raise ValueError(
            f"Contract {contract_id!r} is in state {state!r} and cannot be edited. "
            "Once a contract reaches the signing stage it is legally locked."
        )
