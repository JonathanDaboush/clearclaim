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

def recalculate_log_hash(entry: Any) -> str:
    """Controller for recalculating log hash."""
    return audit_service.recalculate_log_hash(entry)

def generate_audit_snapshot() -> str:
    """Controller for generating audit snapshot."""
    return audit_service.generate_audit_snapshot()

def archive_audit_snapshot(snapshot_hash: str) -> None:
    """Controller for archiving audit snapshot."""
    audit_service.archive_audit_snapshot(snapshot_hash)
