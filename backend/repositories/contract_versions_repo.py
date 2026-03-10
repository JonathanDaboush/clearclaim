import uuid
import datetime
from typing import List, Dict, Set
from models.contract_version_model import ContractVersion


class ContractVersionsRepository:
    _versions: List[ContractVersion] = []   # In-memory (replace with DB in production)
    _approvals: Dict[str, Set[str]] = {}  # version_id -> set of approving user_ids

    @staticmethod
    def create_contract_version(contract_id: str, content: str, created_by: str) -> str:
        """Create a new contract version. Returns the new version ID."""
        version_id = str(uuid.uuid4())
        version = ContractVersion(
            id=version_id,
            contract_id=contract_id,
            content=content,
            created_by=created_by,
            signed=False,
            created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )
        ContractVersionsRepository._versions.append(version)
        ContractVersionsRepository._approvals[version_id] = set()
        return version_id

    @staticmethod
    def add_approval(contract_version_id: str, user_id: str) -> bool:
        """Record a user approval for a contract version. Returns True if version exists."""
        if contract_version_id in ContractVersionsRepository._approvals:
            ContractVersionsRepository._approvals[contract_version_id].add(user_id)
            return True
        return False

    @staticmethod
    def check_unanimous(contract_version_id: str, required_user_ids: Set[str]) -> bool:
        """Return True if all required users have approved the version."""
        approved = ContractVersionsRepository._approvals.get(contract_version_id, set())
        return required_user_ids.issubset(approved)

    @staticmethod
    def mark_signed(contract_version_id: str) -> bool:
        """Mark a contract version as signed. Returns True if found."""
        for version in ContractVersionsRepository._versions:
            if version.id == contract_version_id:
                version.signed = True
                return True
        return False

    @staticmethod
    def get_by_contract(contract_id: str) -> List[ContractVersion]:
        """Return all versions for a given contract."""
        return [v for v in ContractVersionsRepository._versions if v.contract_id == contract_id]
