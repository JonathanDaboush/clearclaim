import uuid
import datetime
from typing import List, Dict, Any


class ContractsRepository:
    _contracts: List[Dict[str, Any]] = []  # In-memory (replace with DB in production)

    @staticmethod
    def create_contract(project_id: str, created_by: str) -> str:
        """Create a new contract record. Returns the new contract ID."""
        contract_id = str(uuid.uuid4())
        ContractsRepository._contracts.append({
            "id": contract_id,
            "project_id": project_id,
            "created_by": created_by,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "current_version": None,
        })
        return contract_id

    @staticmethod
    def update_current_version(contract_id: str, version_id: str) -> bool:
        """Update a contract's current version pointer. Returns True if found."""
        for contract in ContractsRepository._contracts:
            if contract["id"] == contract_id:
                contract["current_version"] = version_id
                return True
        return False

    @staticmethod
    def get_by_id(contract_id: str) -> List[Dict[str, Any]]:
        """Return all contracts matching the given ID."""
        return [c for c in ContractsRepository._contracts if c["id"] == contract_id]
