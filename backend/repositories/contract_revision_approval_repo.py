import uuid
import datetime
from typing import List, Dict, Any
from models.contract_revision_approval_model import ContractRevisionApproval


class ContractRevisionApprovalRepository:
    _approvals: List[ContractRevisionApproval] = []  # In-memory (replace with DB in production)

    def create_approval(self, contract_version_id: str, user_id: str) -> str:
        """Record that a user has approved a contract revision. Returns the approval ID."""
        approval_id = str(uuid.uuid4())
        approval = ContractRevisionApproval(
            id=approval_id,
            contract_version_id=contract_version_id,
            user_id=user_id,
            approved_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )
        self._approvals.append(approval)
        return approval_id

    def get_approval(self, contract_version_id: str, user_id: str) -> Dict[str, Any]:
        """Return the approval record for a specific user and version, or not-approved."""
        for approval in self._approvals:
            if approval.contract_version_id == contract_version_id and approval.user_id == user_id:
                return {"approved": True, "approved_at": approval.approved_at, "id": approval.id}
        return {"approved": False}

    def get_approvals_for_version(self, contract_version_id: str) -> List[Dict[str, Any]]:
        """Return all approval records for a contract version."""
        return [
            {"user_id": a.user_id, "approved_at": a.approved_at, "id": a.id}
            for a in self._approvals if a.contract_version_id == contract_version_id
        ]
