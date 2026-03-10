import uuid
import hashlib
import datetime
from typing import List, Optional
from models.audit_log_model import AuditLog


class AuditRepository:
    _audit_log_chain: List[AuditLog] = []  # Append-only log chain (replace with DB in production)

    @staticmethod
    def log_event(user_id: str, device_id: str, event_type: str, related_object_id: Optional[str] = None, details: Optional[str] = None) -> str:
        """Append a cryptographically chained event to the audit log. Returns the new log ID."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        last_hash = AuditRepository.get_last_hash()
        log_id = str(uuid.uuid4())
        hash_input = f"{log_id}:{user_id}:{device_id}:{event_type}:{related_object_id}:{details}:{timestamp}:{last_hash}"
        log_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        entry = AuditLog(
            id=log_id,
            user_id=user_id,
            device_id=device_id,
            event_type=event_type,
            related_object_id=related_object_id or "",
            details=details or "",
            timestamp=timestamp,
            hash=log_hash,
        )
        AuditRepository._audit_log_chain.append(entry)
        return log_id

    @staticmethod
    def get_last_hash() -> str:
        """Return SHA256 hash of the last log entry, or a genesis hash if the log is empty."""
        if AuditRepository._audit_log_chain:
            return AuditRepository._audit_log_chain[-1].hash
        return hashlib.sha256(b"genesis").hexdigest()

    @classmethod
    def get_chain(cls) -> List[AuditLog]:
        """Return the full audit log chain (read-only view)."""
        return cls._audit_log_chain
