import uuid
import hashlib
import datetime
from typing import List, Dict, Any


class EvidenceRepository:
    _evidence: List[Dict[str, Any]] = []  # In-memory (replace with DB in production)

    ALLOWED_FILE_TYPES = {"pdf", "png", "jpg", "jpeg", "docx"}
    MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

    @staticmethod
    def insert_evidence(contract_id: str, added_by: str, file_url: str, file_type: str | None = None, file_size: int | None = None, hash_value: str | None = None, metadata: Dict[str, Any] | None = None) -> str:
        """Insert a timestamped, hashed evidence record. Returns the new evidence ID."""
        evidence_id = str(uuid.uuid4())
        EvidenceRepository._evidence.append({
            "id": evidence_id,
            "contract_id": contract_id,
            "added_by": added_by,
            "file_url": file_url,
            "file_type": file_type,
            "file_size": file_size,
            "hash_value": hash_value,
            "metadata": metadata,
            "added_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        })
        return evidence_id

    @staticmethod
    def delete_evidence(evidence_id: str) -> bool:
        """Remove an evidence record. Unanimous consent must be enforced at the service layer."""
        for ev in EvidenceRepository._evidence:
            if ev["id"] == evidence_id:
                EvidenceRepository._evidence.remove(ev)
                return True
        return False

    @staticmethod
    def get_by_contract(contract_id: str) -> List[Dict[str, Any]]:
        """Return all evidence records for a given contract."""
        return [e for e in EvidenceRepository._evidence if e["contract_id"] == contract_id]

    @staticmethod
    def validate_file_type(file_type: str | None) -> bool:
        """Return True if the file extension is in the allowed set."""
        return file_type.lower() in EvidenceRepository.ALLOWED_FILE_TYPES if file_type else False

    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Return True if the file is within the maximum allowed size."""
        return 0 < file_size <= EvidenceRepository.MAX_FILE_SIZE_BYTES

    @staticmethod
    def virus_scan(file_bytes: bytes) -> bool:
        """Placeholder for virus scanning integration. Returns True (clean) by default."""
        return True

    @staticmethod
    def calculate_file_hash(file_bytes: bytes) -> str:
        """Return the SHA-256 hash of the file bytes for integrity verification."""
        return hashlib.sha256(file_bytes).hexdigest()

    @staticmethod
    def store_evidence_object(file_bytes: bytes, evidence_id: str) -> bool:
        """Placeholder for object storage (e.g. S3). Returns True on success."""
        return True

    @staticmethod
    def generate_evidence_metadata(file_url: str, file_type: str, file_size: int) -> Dict[str, Any]:
        """Return a metadata dict for an evidence file."""
        return {
            "file_url": file_url,
            "file_type": file_type,
            "file_size": file_size,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

    @staticmethod
    def verify_evidence_integrity(evidence_id: str, expected_hash: str) -> bool:
        """Return True if the stored hash for the evidence matches the expected hash."""
        for ev in EvidenceRepository._evidence:
            if ev["id"] == evidence_id:
                return ev.get("hash_value") == expected_hash
        return False
