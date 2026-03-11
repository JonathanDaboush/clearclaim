import difflib
from typing import List, Dict, Any, Set
from repositories.contracts_repo import ContractsRepository
from repositories.contract_versions_repo import ContractVersionsRepository
from repositories.contract_revision_approval_repo import ContractRevisionApprovalRepository
from services.audit_service import AuditService
from services.notification_service import NotificationService


class ContractService:
    def create_contract(self, project_id: str, created_by: str, content: str) -> Dict[str, Any]:
        """Create a contract and its first version."""
        contract_id = ContractsRepository.create_contract(project_id, created_by)
        version_id = ContractVersionsRepository.create_contract_version(contract_id, content, created_by)
        ContractsRepository.update_current_version(contract_id, version_id)
        AuditService().log_event("create_contract", created_by, {"project_id": project_id, "contract_id": contract_id})
        NotificationService().create_notification(created_by, "contract_created", f"Contract created in project {project_id}.")
        return {"status": "Contract created", "contract_id": contract_id, "version_id": version_id}

    def create_contract_revision(self, contract_id: str, new_content: str, user_id: str) -> Dict[str, Any]:
        """Create a new revision version of a contract, storing a diff in revision_changes."""
        # Fetch current content for diff computation
        from repositories.contract_versions_repo import ContractVersionsRepository as CVR
        existing = CVR.get_by_contract(contract_id)
        old_content = existing[-1].content if existing else ""
        diff_str = self.generate_contract_diff(old_content, new_content)
        version_id = ContractVersionsRepository.create_contract_version(contract_id, new_content, user_id)
        # Store the diff in revision_changes
        import uuid, json, db as _db
        _db.execute(
            "INSERT INTO revision_changes (id, contract_version_id, diff) VALUES (%s, %s, %s)",
            (str(uuid.uuid4()), version_id, json.dumps({"unified_diff": diff_str})),
        )
        AuditService().log_event("create_contract_revision", user_id, {"contract_id": contract_id, "version_id": version_id})
        NotificationService().create_notification(user_id, "revision_created", f"New revision created for contract {contract_id}.")
        return {"status": "Revision created", "version_id": version_id}

    def generate_contract_diff(self, old_content: str, new_content: str) -> str:
        """Return a unified diff string between two contract versions."""
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile="previous",
            tofile="revised",
        )
        return "".join(diff)

    def approve_contract_revision(self, contract_version_id: str, user_id: str) -> Dict[str, Any]:
        """Record a user's approval of a contract revision."""
        approval_repo = ContractRevisionApprovalRepository()
        approval_repo.create_approval(contract_version_id, user_id)
        AuditService().log_event("approve_contract_revision", user_id, {"version_id": contract_version_id})
        NotificationService().create_notification(user_id, "revision_approved", f"You approved revision {contract_version_id}.")
        return {"status": "Revision approved"}

    def check_revision_unanimous_approval(self, contract_version_id: str, required_user_ids: Set[str]) -> bool:
        """Return True if all required parties have approved the revision."""
        return ContractVersionsRepository.check_unanimous(contract_version_id, required_user_ids)

    def activate_contract_version(self, contract_id: str, contract_version_id: str) -> Dict[str, Any]:
        """Set a unanimously approved version as the contract's current version."""
        ContractsRepository.update_current_version(contract_id, contract_version_id)
        AuditService().log_event("activate_contract_version", "system", {"contract_id": contract_id, "version_id": contract_version_id})
        return {"status": "Contract version activated"}

    def get_contract_state(self, contract_id: str) -> str:
        """Return the current state of a contract (draft, active, signed, archived)."""
        from utils.contract_state_utils import get_contract_state
        return get_contract_state(contract_id)

    def transition_contract_state(self, contract_id: str, new_state: str) -> Dict[str, Any]:
        """Transition a contract to a new state and audit log the change."""
        from utils.contract_state_utils import transition_contract_state
        transition_contract_state(contract_id, new_state)
        AuditService().log_event("state_transition", "system", {"contract_id": contract_id, "new_state": new_state})
        return {"status": f"Contract transitioned to {new_state}"}

    def get_contract_versions(self, contract_id: str) -> List[Dict[str, Any]]:
        """Return all versions for a contract."""
        return [vars(v) for v in ContractVersionsRepository.get_by_contract(contract_id)]
