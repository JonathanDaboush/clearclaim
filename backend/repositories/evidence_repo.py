import uuid
import hashlib
import datetime
import json
from typing import Any, Dict, List, Optional
import db


class EvidenceRepository:
    ALLOWED_FILE_TYPES = {"pdf", "png", "jpg", "jpeg", "docx"}
    MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

    @staticmethod
    def insert_evidence(
        contract_id: str,
        added_by: str,
        file_url: str,
        file_type: Optional[str] = None,
        file_size: Optional[int] = None,
        hash_value: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        evidence_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO evidence (id, contract_id, added_by, file_url, file_type, file_size, hash_value, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                evidence_id,
                contract_id,
                added_by,
                file_url,
                file_type,
                file_size,
                hash_value,
                json.dumps(metadata) if isinstance(metadata, dict) else metadata,
            ),
        )
        return evidence_id

    @staticmethod
    def delete_evidence(evidence_id: str) -> bool:
        rows = db.query("SELECT id FROM evidence WHERE id = %s", (evidence_id,))
        if not rows:
            return False
        db.execute("DELETE FROM evidence WHERE id = %s", (evidence_id,))
        return True

    @staticmethod
    def get_by_contract(contract_id: str) -> List[Dict[str, Any]]:
        return db.query(
            "SELECT id, contract_id, added_by, file_url, file_type, file_size, hash_value, metadata, status, added_at::text AS added_at FROM evidence WHERE contract_id = %s ORDER BY added_at",
            (contract_id,),
        )

    @staticmethod
    def validate_file_type(file_type: Optional[str]) -> bool:
        return file_type.lower() in EvidenceRepository.ALLOWED_FILE_TYPES if file_type else False

    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        return 0 < file_size <= EvidenceRepository.MAX_FILE_SIZE_BYTES

    @staticmethod
    def virus_scan(file_bytes: bytes) -> bool:
        return True  # Placeholder for real AV integration

    @staticmethod
    def calculate_file_hash(file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()

    @staticmethod
    def store_evidence_object(file_bytes: bytes, evidence_id: str) -> bool:
        return True  # Placeholder for object storage (e.g. S3)

    @staticmethod
    def generate_evidence_metadata(file_url: str, file_type: str, file_size: int) -> Dict[str, Any]:
        return {
            "file_url": file_url,
            "file_type": file_type,
            "file_size": file_size,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

    @staticmethod
    def verify_evidence_integrity(evidence_id: str, expected_hash: str) -> bool:
        rows = db.query("SELECT hash_value FROM evidence WHERE id = %s", (evidence_id,))
        if not rows:
            return False
        return rows[0]["hash_value"] == expected_hash
