import uuid
import hashlib
from typing import Any, Dict, List, Optional, Set
import db
from models.contract_version_model import ContractVersion


class ContractVersionsRepository:

    @staticmethod
    def _to_obj(row: Dict[str, Any]) -> ContractVersion:
        return ContractVersion(
            id=row["id"],
            contract_id=row["contract_id"],
            content=row["content"],
            created_by=row["created_by"],
            signed=bool(row.get("signed", False)),
            created_at=str(row.get("created_at", "")),
            version_number=int(row.get("version_number", 1)),
            content_hash=row.get("content_hash", ""),
        )

    @staticmethod
    def create_contract_version(contract_id: str, content: str, created_by: str) -> str:
        version_id = str(uuid.uuid4())
        # auto-increment version_number per contract
        rows = db.query(
            "SELECT COALESCE(MAX(version_number), 0) AS mx FROM contract_versions WHERE contract_id = %s",
            (contract_id,),
        )
        next_num = int(rows[0]["mx"]) + 1 if rows else 1
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        db.execute(
            "INSERT INTO contract_versions (id, contract_id, content, created_by, version_number, content_hash) VALUES (%s, %s, %s, %s, %s, %s)",
            (version_id, contract_id, content, created_by, next_num, content_hash),
        )
        return version_id

    @staticmethod
    def add_approval(contract_version_id: str, user_id: str) -> bool:
        approval_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO contract_version_approvals (id, contract_version_id, user_id) VALUES (%s, %s, %s) ON CONFLICT (contract_version_id, user_id) DO NOTHING",
            (approval_id, contract_version_id, user_id),
        )
        return True

    @staticmethod
    def check_unanimous(contract_version_id: str, required_user_ids) -> bool:
        if not required_user_ids:
            return True
        required = set(required_user_ids)
        rows = db.query(
            "SELECT user_id FROM contract_revision_approvals WHERE contract_version_id = %s",
            (contract_version_id,),
        )
        approved = {r["user_id"] for r in rows}
        return required.issubset(approved)

    @staticmethod
    def mark_signed(contract_version_id: str) -> bool:
        rows = db.query("SELECT id FROM contract_versions WHERE id = %s", (contract_version_id,))
        if not rows:
            return False
        db.execute("UPDATE contract_versions SET signed = TRUE WHERE id = %s", (contract_version_id,))
        return True

    @staticmethod
    def get_by_contract(contract_id: str) -> List[ContractVersion]:
        rows = db.query(
            "SELECT id, contract_id, content, created_by, version_number, content_hash, signed, created_at::text AS created_at FROM contract_versions WHERE contract_id = %s ORDER BY version_number",
            (contract_id,),
        )
        return [ContractVersionsRepository._to_obj(r) for r in rows]

    @staticmethod
    def get_by_id(version_id: str) -> Optional[ContractVersion]:
        rows = db.query(
            "SELECT id, contract_id, content, created_by, version_number, content_hash, signed, created_at::text AS created_at FROM contract_versions WHERE id = %s",
            (version_id,),
        )
        return ContractVersionsRepository._to_obj(rows[0]) if rows else None
