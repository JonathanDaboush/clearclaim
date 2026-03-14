"""Typed domain events and their default listeners.

Import this module at startup (it is imported via main.py) so that all
listeners are registered before the first request arrives.

Adding a new event:
  1. Define a dataclass here.
  2. Publish it from the relevant service.
  3. Optionally register listeners below with @event_bus.subscribe(YourEvent).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from events.event_bus import event_bus

logger = logging.getLogger(__name__)


# ── Event definitions ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ProjectCreated:
    project_id: str
    name: str
    created_by: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class ContractCreated:
    contract_id: str
    project_id: str
    created_by: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class ContractStateChanged:
    contract_id: str
    from_state: str
    to_state: str
    changed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class ContractSigned:
    contract_id: str
    version_id: str
    user_id: str
    device_id: str
    signature_id: str
    signed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class EvidenceUploaded:
    evidence_id: str
    contract_id: str
    added_by: str
    file_hash: str
    timestamp_proof: str
    uploaded_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class MemberAdded:
    project_id: str
    user_id: str
    role: str
    added_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class PaymentRecorded:
    user_id: str
    payment_id: str
    amount: float
    method: str
    recorded_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class SecurityBreachDetected:
    user_id: str
    event_type: str
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ── Default listeners ─────────────────────────────────────────────────────────
# These listeners implement cross-cutting concerns (audit, notifications) so
# individual services can stay decoupled from each other.

@event_bus.subscribe(ProjectCreated)
def _on_project_created(event: ProjectCreated) -> None:
    logger.info("Project %s ('%s') created by %s", event.project_id, event.name, event.created_by)


@event_bus.subscribe(MemberAdded)
def _on_member_added(event: MemberAdded) -> None:
    logger.info("User %s added to project %s as %s", event.user_id, event.project_id, event.role)


@event_bus.subscribe(ContractStateChanged)
def _on_contract_state_changed(event: ContractStateChanged) -> None:
    logger.info(
        "Contract %s state: %s → %s",
        event.contract_id, event.from_state, event.to_state,
    )


@event_bus.subscribe(ContractSigned)
def _on_contract_signed(event: ContractSigned) -> None:
    logger.info(
        "Contract %s version %s signed by user %s",
        event.contract_id, event.version_id, event.user_id,
    )


@event_bus.subscribe(SecurityBreachDetected)
def _on_breach(event: SecurityBreachDetected) -> None:
    logger.warning(
        "Security breach detected for user %s: %s",
        event.user_id, event.event_type,
    )
