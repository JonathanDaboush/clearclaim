# AuditController calls AuditService
from typing import Dict, Any
from services.audit_service import AuditService

audit_service = AuditService()

def log_event(event_type: str, user_id: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """Controller for logging event.
    Ensures logs are immutable and retained for compliance.
    Triggers breach notification if event_type is 'breach'."""
    return audit_service.log_event(event_type, user_id, details)

def get_previous_log_hash() -> str:
    """Controller for getting previous log hash."""
    return audit_service.get_previous_log_hash()

def generate_log_hash(prev_hash: str, event_data: Dict[str, Any]) -> str:
    """Controller for generating log hash."""
    return audit_service.generate_log_hash(prev_hash, event_data)

def append_audit_log(event_data: Dict[str, Any]) -> str:
    """Controller for appending audit log."""
    return audit_service.append_audit_log(event_data)

def verify_audit_chain() -> bool:
    """Controller for verifying audit chain."""
    return audit_service.verify_audit_chain()

def verify_audit_entries() -> Dict[str, Any]:
    """Controller for per-entry audit chain integrity verification."""
    return audit_service.verify_audit_entries()

def recalculate_log_hash(entry: Any) -> str:
    """Controller for recalculating log hash."""
    return audit_service.recalculate_log_hash(entry)

def generate_audit_snapshot() -> str:
    """Controller for generating audit snapshot."""
    return audit_service.generate_audit_snapshot()

def archive_audit_snapshot(snapshot_hash: str) -> None:
    """Controller for archiving audit snapshot."""
    audit_service.archive_audit_snapshot(snapshot_hash)

def get_audit_entries(related_object_id: str = "", limit: str = "50") -> list:
    """Return audit log entries, optionally filtered by related_object_id."""
    from repositories.audit_repo import AuditRepository
    try:
        n = int(limit)
    except (ValueError, TypeError):
        n = 50
    entries = AuditRepository.get_chain(
        related_object_id=related_object_id or None,
        limit=n,
    )
    return [
        {
            "id": e.id,
            "user_id": e.user_id,
            "device_id": e.device_id,
            "event_type": e.event_type,
            "related_object_id": e.related_object_id,
            "contract_id": e.contract_id,
            "contract_version_id": e.contract_version_id,
            "details": e.details,
            "timestamp": e.timestamp,
            "prev_hash": e.prev_hash,
            "hash": e.hash,
            "snapshot_hash": e.snapshot_hash,
        }
        for e in entries
    ]
