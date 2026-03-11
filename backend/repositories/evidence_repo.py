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
        # also populate the evidence_contracts join table (spec §13)
        ec_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO evidence_contracts (id, evidence_id, contract_id) VALUES (%s, %s, %s) ON CONFLICT (evidence_id, contract_id) DO NOTHING",
            (ec_id, evidence_id, contract_id),
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

    @staticmethod
    def get_by_user(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Return recent evidence from projects the user is a member of."""
        return db.query(
            """
            SELECT DISTINCT e.id, e.contract_id, e.added_by,
                   e.file_url, e.file_type, e.file_size,
                   e.hash_value, e.metadata, e.status,
                   e.added_at::text AS added_at
            FROM evidence e
            JOIN contracts c ON c.id = e.contract_id
            JOIN memberships m ON m.project_id = c.project_id
            WHERE m.user_id = %s AND m.soft_deleted = FALSE
            ORDER BY e.added_at DESC
            LIMIT %s
            """,
            (user_id, limit),
        )
