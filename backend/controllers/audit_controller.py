# AuditController calls AuditService
from services.audit_service import AuditService

audit_service = AuditService()

def log_event(event_type, user_id, details):
    """Controller for logging event."""
    return audit_service.log_event(event_type, user_id, details)

def get_previous_log_hash():
    """Controller for getting previous log hash."""
    return audit_service.get_previous_log_hash()

def generate_log_hash(prev_hash, event_data):
    """Controller for generating log hash."""
    return audit_service.generate_log_hash(prev_hash, event_data)

def append_audit_log(event_data):
    """Controller for appending audit log."""
    return audit_service.append_audit_log(event_data)

def verify_audit_chain():
    """Controller for verifying audit chain."""
    return audit_service.verify_audit_chain()

def recalculate_log_hash(entry):
    """Controller for recalculating log hash."""
    return audit_service.recalculate_log_hash(entry)

def generate_audit_snapshot():
    """Controller for generating audit snapshot."""
    return audit_service.generate_audit_snapshot()

def archive_audit_snapshot(snapshot):
    """Controller for archiving audit snapshot."""
    return audit_service.archive_audit_snapshot(snapshot)
