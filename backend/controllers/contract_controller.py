# ContractController calls ContractService
from services.contract_service import ContractService

contract_service = ContractService()
# ContractController handler functions
def create_contract(project_id, created_by, content):
    """Controller for creating contract."""
    return contract_service.create_contract(project_id, created_by, content)

def create_contract_revision(contract_id, new_content, user_id):
    """Controller for creating contract revision."""
    return contract_service.create_contract_revision(contract_id, new_content, user_id)

def generate_contract_diff(old_content, new_content):
    """Controller for generating contract diff."""
    return contract_service.generate_contract_diff(old_content, new_content)

def approve_contract_revision(contract_version_id, user_id):
    """Controller for approving contract revision."""
    return contract_service.approve_contract_revision(contract_version_id, user_id)

def check_revision_unanimous_approval(contract_version_id):
    """Controller for checking revision unanimous approval."""
    return contract_service.check_revision_unanimous_approval(contract_version_id)
def activate_contract_version(contract_version_id):
    """Controller for activating contract version."""
    return contract_service.activate_contract_version(contract_version_id)
def get_contract_state(contract_id):
    """Controller for getting contract state."""
    return contract_service.get_contract_state(contract_id)
def transition_contract_state(contract_id, new_state):
    """Controller for transitioning contract state."""
    return contract_service.transition_contract_state(contract_id, new_state)
def get_contract_versions(contract_id):
    """Controller for getting contract versions."""
    return contract_service.get_contract_versions(contract_id)
