import uuid
from typing import Any, Dict, List
import db


class ContractRevisionApprovalRepository:

    def create_approval(self, contract_version_id: str, user_id: str) -> str:
        approval_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO contract_revision_approvals (id, contract_version_id, user_id) VALUES (%s, %s, %s)",
            (approval_id, contract_version_id, user_id),
        )
        return approval_id

    def get_approval(self, contract_version_id: str, user_id: str) -> Dict[str, Any]:
        rows = db.query(
            "SELECT id, approved_at::text AS approved_at FROM contract_revision_approvals WHERE contract_version_id = %s AND user_id = %s LIMIT 1",
            (contract_version_id, user_id),
        )
        if rows:
            return {"approved": True, "approved_at": rows[0]["approved_at"], "id": rows[0]["id"]}
        return {"approved": False}

    def get_approvals_for_version(self, contract_version_id: str) -> List[Dict[str, Any]]:
        rows = db.query(
            "SELECT id, user_id, approved_at::text AS approved_at FROM contract_revision_approvals WHERE contract_version_id = %s",
            (contract_version_id,),
        )
        return [{"user_id": r["user_id"], "approved_at": r["approved_at"], "id": r["id"]} for r in rows]
