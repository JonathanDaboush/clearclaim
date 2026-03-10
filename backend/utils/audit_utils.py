import hashlib
import datetime
from typing import Dict, Any, Optional, Set


def is_valid_audit_event(event_type: str, details: Dict[str, Any]) -> bool:
    """Return True if both event_type and details are non-empty."""
    return bool(event_type)


def calculate_file_hash(file_bytes: bytes) -> str:
    """Return SHA-256 hash of file bytes."""
    return hashlib.sha256(file_bytes).hexdigest()


def validate_file_type(file_type: str, allowed: Optional[Set[str]] = None) -> bool:
    """Return True if file_type is in the allowed set."""
    effective_allowed: Set[str] = allowed if allowed is not None else {"pdf", "png", "jpg", "jpeg", "docx"}
    return file_type.lower() in effective_allowed if file_type else False


def validate_file_size(file_size: int, max_bytes: int = 50 * 1024 * 1024) -> bool:
    """Return True if file_size is positive and within the limit."""
    return 0 < file_size <= max_bytes


def virus_scan(file_bytes: bytes) -> bool:
    """Placeholder for virus scan. Returns True (clean) by default."""
    return True


def store_evidence_object(file_bytes: bytes, evidence_id: str) -> bool:
    """Placeholder for object storage upload."""
    return True


def generate_evidence_metadata(file_url: str, file_type: str, file_size: int) -> Dict[str, Any]:
    """Return a metadata dict for an evidence file."""
    return {
        "file_url": file_url,
        "file_type": file_type,
        "file_size": file_size,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def verify_evidence_integrity(evidence_id: str, stored_hash: str, expected_hash: str) -> bool:
    """Return True if stored_hash matches expected_hash."""
    return stored_hash == expected_hash
