import uuid
import hashlib
import datetime
from typing import Any, List, Optional
import db
from models.audit_log_model import AuditLog


class AuditRepository:

    @staticmethod
    def log_event(
        user_id: str,
        device_id: str,
        event_type: str,
        related_object_id: Optional[str] = None,
        details: Optional[str] = None,
        contract_id: str = '',
        contract_version_id: str = '',
    ) -> str:
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        prev_hash = AuditRepository.get_last_hash()
        log_id = str(uuid.uuid4())
        hash_input = f"{log_id}:{user_id}:{device_id}:{event_type}:{related_object_id}:{details}:{timestamp}:{prev_hash}"
        log_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        db.execute(
            "INSERT INTO audit_logs (id, user_id, device_id, event_type, related_object_id, contract_id, contract_version_id, details, timestamp, prev_hash, hash) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                log_id,
                user_id,
                device_id or "",
                event_type,
                related_object_id or "",
                contract_id or "",
                contract_version_id or "",
                details or "",
                timestamp,
                prev_hash,
                log_hash,
            ),
        )
        return log_id

    @staticmethod
    def get_last_hash() -> str:
        rows = db.query("SELECT hash FROM audit_logs ORDER BY timestamp DESC LIMIT 1")
        if rows:
            return rows[0]["hash"]
        return hashlib.sha256(b"genesis").hexdigest()

    @staticmethod
    def get_chain(
        related_object_id: Optional[str] = None,
        limit: int = 500,
    ) -> List[AuditLog]:
        if related_object_id:
            rows = db.query(
                "SELECT id, user_id, device_id, event_type, related_object_id, contract_id, contract_version_id, details, timestamp, prev_hash, hash, snapshot_hash FROM audit_logs WHERE related_object_id = %s ORDER BY timestamp ASC LIMIT %s",
                (related_object_id, limit),
            )
        else:
            rows = db.query(
                "SELECT id, user_id, device_id, event_type, related_object_id, contract_id, contract_version_id, details, timestamp, prev_hash, hash, snapshot_hash FROM audit_logs ORDER BY timestamp ASC LIMIT %s",
                (limit,),
            )
        return [
            AuditLog(
                id=r["id"],
                user_id=r["user_id"],
                device_id=r["device_id"],
                event_type=r["event_type"],
                related_object_id=r["related_object_id"],
                details=r["details"],
                timestamp=r["timestamp"],
                hash=r["hash"],
                prev_hash=r.get("prev_hash", ""),
                contract_id=r.get("contract_id", ""),
                contract_version_id=r.get("contract_version_id", ""),
                snapshot_hash=r.get("snapshot_hash", ""),
            )
            for r in rows
        ]
