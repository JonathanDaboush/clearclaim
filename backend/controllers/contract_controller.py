# ContractController calls ContractService
from typing import Dict, Any, List, Set
from services.contract_service import ContractService

contract_service = ContractService()

def create_contract(project_id: str, created_by: str, content: str) -> Dict[str, Any]:
    """Controller for creating contract."""
    return contract_service.create_contract(project_id, created_by, content)

def create_contract_revision(contract_id: str, new_content: str, user_id: str) -> Dict[str, Any]:
    """Controller for creating contract revision."""
    return contract_service.create_contract_revision(contract_id, new_content, user_id)

def generate_contract_diff(old_content: str, new_content: str) -> str:
    """Controller for generating contract diff."""
    return contract_service.generate_contract_diff(old_content, new_content)

def approve_contract_revision(contract_version_id: str, user_id: str) -> Dict[str, Any]:
    """Controller for approving contract revision."""
    return contract_service.approve_contract_revision(contract_version_id, user_id)

def check_revision_unanimous_approval(contract_version_id: str, required_user_ids: Set[str]) -> bool:
    """Controller for checking revision unanimous approval."""
    return contract_service.check_revision_unanimous_approval(contract_version_id, required_user_ids)

def activate_contract_version(contract_id: str, contract_version_id: str) -> Dict[str, Any]:
    """Controller for activating contract version."""
    return contract_service.activate_contract_version(contract_id, contract_version_id)

def get_contract_state(contract_id: str) -> str:
    """Controller for getting contract state."""
    return contract_service.get_contract_state(contract_id)

def transition_contract_state(contract_id: str, new_state: str) -> Dict[str, Any]:
    """Controller for transitioning contract state."""
    return contract_service.transition_contract_state(contract_id, new_state)

def get_contract_versions(contract_id: str) -> List[Dict[str, Any]]:
    """Controller for getting contract versions."""
    return contract_service.get_contract_versions(contract_id)

def get_contract(contract_id: str) -> Dict[str, Any]:
    """Return a single contract record by ID."""
    from repositories.contracts_repo import ContractsRepository
    matches = ContractsRepository.get_by_id(contract_id)
    if not matches:
        return {"error": "Contract not found"}
    return matches[0]

def get_project_contracts(project_id: str) -> List[Dict[str, Any]]:
    """Return all contracts belonging to a project."""
    from repositories.contracts_repo import ContractsRepository
    return ContractsRepository.get_by_project(project_id)
