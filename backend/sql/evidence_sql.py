import hashlib
import datetime
from typing import Dict, Any, Optional


class EvidenceSQL:
    ALLOWED_FILE_TYPES = {"pdf", "png", "jpg", "jpeg", "docx"}
    MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

    def insert_evidence(self, contract_id: str, added_by: str, file_url: str, file_type: Optional[str] = None, file_size: Optional[int] = None, hash_value: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Build the SQL INSERT dict for an evidence record. Returns the values as a dict."""
        import uuid
        return str(uuid.uuid4())  # In production: delegate to SQLTemplate.insert(...)

    def delete_evidence(self, evidence_id: str) -> bool:
        """Build the SQL DELETE for an evidence record. Returns True on success."""
        return True  # In production: delegate to SQLTemplate.delete(...)

    def validate_file_type(self, file_type: str) -> bool:
        """Return True if the file extension is allowed."""
        return file_type.lower() in self.ALLOWED_FILE_TYPES if file_type else False

    def validate_file_size(self, file_size: int) -> bool:
        """Return True if file_size is within the allowed limit."""
        return 0 < file_size <= self.MAX_FILE_SIZE_BYTES

    def virus_scan(self, file_bytes: bytes) -> bool:
        """Placeholder for virus scan integration. Returns True (clean)."""
        return True

    def calculate_file_hash(self, file_bytes: bytes) -> str:
        """Return the SHA-256 hash of file bytes."""
        return hashlib.sha256(file_bytes).hexdigest()

    def store_evidence_object(self, file_bytes: bytes, evidence_id: str) -> bool:
        """Placeholder for object storage upload. Returns True on success."""
        return True

    def generate_evidence_metadata(self, file_url: str, file_type: str, file_size: int) -> Dict[str, Any]:
        """Return a metadata dict for an evidence file."""
        return {
            "file_url": file_url,
            "file_type": file_type,
            "file_size": file_size,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

    def verify_evidence_integrity(self, evidence_id: str, expected_hash: str) -> bool:
        """Return True if the stored hash matches expected_hash (stub: always True)."""
        return True  # In production: fetch hash from DB and compare
