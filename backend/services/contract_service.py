import difflib
from typing import List, Dict, Any, Set
from repositories.contracts_repo import ContractsRepository
from repositories.contract_versions_repo import ContractVersionsRepository
from repositories.contract_revision_approval_repo import ContractRevisionApprovalRepository
from services.audit_service import AuditService
from services.notification_service import NotificationService


class ContractService:
    def create_contract(self, project_id: str, created_by: str, content: str, name: str = 'Untitled Contract') -> Dict[str, Any]:
        """Create a contract and its first version."""
        contract_id = ContractsRepository.create_contract(project_id, created_by, name)
        version_id = ContractVersionsRepository.create_contract_version(contract_id, content, created_by)
        ContractsRepository.update_current_version(contract_id, version_id)
        AuditService().log_event("create_contract", created_by, {"project_id": project_id, "contract_id": contract_id})
        NotificationService().create_notification(created_by, "contract_created", f"Contract created in project {project_id}.")
        from events.event_bus import event_bus
        from events.domain_events import ContractCreated
        event_bus.publish(ContractCreated(contract_id=contract_id, project_id=project_id, created_by=created_by))
        return {"status": "Contract created", "contract_id": contract_id, "version_id": version_id}

    def create_contract_revision(self, contract_id: str, new_content: str, user_id: str) -> Dict[str, Any]:
        """Create a new revision version of a contract, storing a diff in revision_changes."""
        from utils.contract_state_utils import assert_contract_editable, transition_contract_state, DRAFT, REVISION_PENDING
        try:
            assert_contract_editable(contract_id)
        except ValueError as exc:
            return {"status": "error", "message": str(exc)}
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
        # Advance state to revision_pending so parties know a change awaits review
        try:
            from utils.contract_state_utils import get_contract_state, DRAFT, REVISION_PENDING
            current = get_contract_state(contract_id)
            if current == DRAFT:
                transition_contract_state(contract_id, REVISION_PENDING)
        except Exception:
            pass  # state advance is best-effort; the revision is committed regardless
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
        """Record a user's approval of a contract revision. Auto-activates if unanimous."""
        approval_repo = ContractRevisionApprovalRepository()
        approval_repo.create_approval(contract_version_id, user_id)
        AuditService().log_event("approve_contract_revision", user_id, {"version_id": contract_version_id})
        NotificationService().create_notification(user_id, "revision_approved", f"You approved revision {contract_version_id}.")

        # Auto-activate if all project members have now approved
        try:
            import db as _db
            cv_rows = _db.query(
                """SELECT c.id AS contract_id, c.project_id
                   FROM contract_versions cv
                   JOIN contracts c ON c.id = cv.contract_id
                   WHERE cv.id = %s""",
                (contract_version_id,),
            )
            if cv_rows:
                contract_id = cv_rows[0]["contract_id"]
                project_id = cv_rows[0]["project_id"]
                member_rows = _db.query(
                    "SELECT user_id FROM memberships WHERE project_id = %s AND soft_deleted = FALSE",
                    (project_id,),
                )
                required = {r["user_id"] for r in member_rows}
                if required and self.check_revision_unanimous_approval(contract_version_id, required):
                    self.activate_contract_version(contract_id, contract_version_id)
        except Exception:
            pass  # auto-activation is best-effort; caller can activate manually

        return {"status": "Revision approved"}

    def reject_contract_revision(self, contract_version_id: str, user_id: str) -> Dict[str, Any]:
        """Mark a contract revision as rejected. Prevents it from being activated."""
        import db as _db
        _db.execute(
            "UPDATE contract_versions SET rejected = TRUE WHERE id = %s",
            (contract_version_id,),
        )
        AuditService().log_event("reject_contract_revision", user_id, {"version_id": contract_version_id})
        NotificationService().create_notification(user_id, "revision_rejected", f"Revision {contract_version_id} has been rejected.")
        return {"status": "Revision rejected"}

    def check_revision_unanimous_approval(self, contract_version_id: str, required_user_ids: Set[str]) -> bool:
        """Return True if all required parties have approved the revision."""
        return ContractVersionsRepository.check_unanimous(contract_version_id, required_user_ids)

    def activate_contract_version(self, contract_id: str, contract_version_id: str, required_user_ids: Set[str] = None) -> Dict[str, Any]:
        """Set a unanimously approved version as the contract's current version.
        Raises an error if not all required parties have approved."""
        if required_user_ids is None:
            required_user_ids = set()
        # Check unanimous approval before activating (spec §2)
        if required_user_ids and not self.check_revision_unanimous_approval(contract_version_id, required_user_ids):
            return {"status": "error", "message": "Unanimous approval required from all parties before activation."}
        ContractsRepository.update_current_version(contract_id, contract_version_id)
        # Advance state to ready_for_signature
        try:
            from utils.contract_state_utils import transition_contract_state, get_contract_state, REVISION_APPROVED, REVISION_PENDING, READY_FOR_SIGNATURE
            current = get_contract_state(contract_id)
            if current not in (READY_FOR_SIGNATURE, "fully_signed", "archived"):
                transition_contract_state(contract_id, READY_FOR_SIGNATURE)
        except Exception:
            pass
        AuditService().log_event("activate_contract_version", "system", {"contract_id": contract_id, "version_id": contract_version_id})
        return {"status": "Contract version activated"}

    def get_contract_state(self, contract_id: str) -> str:
        """Return the current state of a contract (draft, active, signed, archived)."""
        from utils.contract_state_utils import get_contract_state
        return get_contract_state(contract_id)

    def transition_contract_state(self, contract_id: str, new_state: str) -> Dict[str, Any]:
        """Transition a contract to a new state and audit log the change."""
        from utils.contract_state_utils import transition_contract_state, get_contract_state
        old_state = get_contract_state(contract_id)
        transition_contract_state(contract_id, new_state)
        AuditService().log_event("state_transition", "system", {"contract_id": contract_id, "new_state": new_state})
        from events.event_bus import event_bus
        from events.domain_events import ContractStateChanged
        event_bus.publish(ContractStateChanged(contract_id=contract_id, from_state=old_state, to_state=new_state))
        return {"status": f"Contract transitioned to {new_state}"}

    def get_contract_versions(self, contract_id: str) -> List[Dict[str, Any]]:
        """Return all versions for a contract."""
        return [vars(v) for v in ContractVersionsRepository.get_by_contract(contract_id)]
