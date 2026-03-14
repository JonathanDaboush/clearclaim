import uuid
from typing import Any, Dict, List, Optional, Set
import db
from models.signature_model import Signature


class SignatureRepository:

    @staticmethod
    def _to_obj(row: Dict[str, Any]) -> Signature:
        return Signature(
            id=row["id"],
            contract_version_id=row["contract_version_id"],
            user_id=row["user_id"],
            device_id=row["device_id"],
            signed_at=row["signed_at"],
            signature_hash=row.get("signature_hash", ""),
            image_url=row.get("image_url"),
            ip=row.get("ip", ""),
        )

    @staticmethod
    def insert_signature(
        contract_version_id: str,
        user_id: str,
        device_id: str,
        signed_at: str,
        signature_hash: str = "",
        image_url: Optional[str] = None,
        ip: str = "",
        contract_snapshot_hash: str = "",
        totp_verified: bool = False,
        user_agent: str = "",
    ) -> str:
        signature_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO signatures
              (id, contract_version_id, user_id, device_id, signed_at,
               signature_hash, image_url, ip,
               contract_snapshot_hash, totp_verified, user_agent)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (signature_id, contract_version_id, user_id, device_id, signed_at,
             signature_hash, image_url, ip,
             contract_snapshot_hash, totp_verified, user_agent),
        )
        return signature_id

    @staticmethod
    def delete_signature(signature_id: str) -> bool:
        rows = db.query("SELECT id FROM signatures WHERE id = %s", (signature_id,))
        if not rows:
            return False
        db.execute("DELETE FROM signatures WHERE id = %s", (signature_id,))
        return True

    @staticmethod
    def get_by_version_ids(version_ids: Set[str]) -> List[Signature]:
        if not version_ids:
            return []
        placeholders = ",".join(["%s"] * len(version_ids))
        rows = db.query(
            f"SELECT id, contract_version_id, user_id, device_id, signed_at, signature_hash, image_url, ip FROM signatures WHERE contract_version_id IN ({placeholders})",
            tuple(version_ids),
        )
        return [SignatureRepository._to_obj(r) for r in rows]
