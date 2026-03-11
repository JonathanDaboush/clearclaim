import hashlib
from typing import Dict

class AuditLog:
    def __init__(self, id: str, user_id: str, device_id: str, event_type: str, related_object_id: str, details: str, timestamp: str, hash: str, prev_hash: str = '', contract_id: str = '', contract_version_id: str = '', snapshot_hash: str = ''):
        self.id = id
        self.user_id = user_id
        self.device_id = device_id
        self.event_type = event_type
        self.related_object_id = related_object_id
        self.details = details
        self.timestamp = timestamp
        self.hash = hash
        self.prev_hash = prev_hash
        self.contract_id = contract_id
        self.contract_version_id = contract_version_id
        self.snapshot_hash = snapshot_hash

    def validate_event(self, event_type: str, details: Dict[str, object]) -> bool:
        return bool(event_type and details)

    def generate_audit_hash(self, *args: object) -> str:
        hash_input = ':'.join(str(arg) for arg in args).encode()
        return hashlib.sha256(hash_input).hexdigest()
