import hashlib
from typing import Dict, Any
from repositories.audit_repo import AuditRepository
from services.notification_service import NotificationService


class AuditService:
    def log_event(self, event_type: str, user_id: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Append a cryptographically chained event to the audit log.
        Automatically sends a breach notification when event_type is 'breach'."""
        if event_type == "breach":
            NotificationService().create_notification(user_id, "breach", "A breach event was logged.")
        log_id = AuditRepository.log_event(
            user_id=user_id,
            device_id=str(details.get("device_id") or ""),
            event_type=event_type,
            related_object_id=str(details.get("related_object_id") or details.get("contract_id") or details.get("evidence_id") or details.get("version_id") or "") or None,
            details=str(details),
            contract_id=str(details.get("contract_id") or ""),
            contract_version_id=str(details.get("version_id") or details.get("contract_version_id") or ""),
        )
        return {"status": "Event logged", "log_id": log_id}

    def get_previous_log_hash(self) -> str:
        """Return the hash of the last audit log entry."""
        return AuditRepository.get_last_hash()

    def generate_log_hash(self, prev_hash: str, event_data: Dict[str, Any]) -> str:
        """Generate a SHA-256 hash chaining prev_hash with serialised event data."""
        payload = f"{prev_hash}:{event_data}".encode()
        return hashlib.sha256(payload).hexdigest()

    def append_audit_log(self, event_data: Dict[str, Any]) -> str:
        """Build and append a new audit log entry from a raw event dict."""
        return AuditRepository.log_event(
            user_id=str(event_data.get("user_id") or ""),
            device_id=str(event_data.get("device_id") or ""),
            event_type=str(event_data.get("event_type") or ""),
            related_object_id=str(event_data.get("related_object_id") or "") or None,
            details=str(event_data.get("details")),
        )

    def verify_audit_chain(self) -> bool:
        """Walk the in-memory audit chain and verify each entry's hash is consistent."""
        chain = AuditRepository.get_chain()
        if not chain:
            return True
        import hashlib as _hl
        genesis = _hl.sha256(b"genesis").hexdigest()
        for i, entry in enumerate(chain):
            if i == 0:
                expected_prev = genesis
            else:
                expected_prev = chain[i - 1].hash
            payload = f"{entry.id}:{entry.user_id}:{entry.device_id}:{entry.event_type}:{entry.related_object_id}:{entry.details}:{entry.timestamp}:{expected_prev}"
            expected_hash = _hl.sha256(payload.encode()).hexdigest()
            if entry.hash != expected_hash:
                return False
        return True

    def recalculate_log_hash(self, entry: Any) -> str:
        """Recalculate the hash for a given AuditLog entry (for verification purposes)."""
        import hashlib as _hl
        prev_hash = AuditRepository.get_last_hash()
        payload = f"{entry.id}:{entry.user_id}:{entry.device_id}:{entry.event_type}:{entry.related_object_id}:{entry.details}:{entry.timestamp}:{prev_hash}"
        return _hl.sha256(payload.encode()).hexdigest()

    def generate_audit_snapshot(self) -> str:
        """Hash the entire current audit chain as a snapshot for external anchoring."""
        import hashlib as _hl
        chain_data = "".join(e.hash for e in AuditRepository.get_chain())
        return _hl.sha256(chain_data.encode()).hexdigest()

    def archive_audit_snapshot(self, snapshot_hash: str):
        """Pass the snapshot hash to the async anchoring task for external archiving."""
        from services.async_tasks import AsyncTasks
        AsyncTasks.anchor_audit_snapshot_async(snapshot_hash)
        return {"status": "Snapshot archived", "snapshot_hash": snapshot_hash}
