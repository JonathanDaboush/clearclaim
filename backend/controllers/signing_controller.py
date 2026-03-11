# SigningController calls SigningService
from typing import Dict, Any, Set
from services.signing_service import SigningService

signing_service = SigningService()

def request_signature(contract_version_id: str, user_id: str) -> Dict[str, Any]:
    """Controller for requesting signature."""
    return signing_service.request_signature(contract_version_id, user_id)

def verify_signing_totp(totp_secret: str, code: str) -> bool:
    """Controller for verifying signing TOTP."""
    return signing_service.verify_signing_totp(totp_secret, code)

def sign_contract(contract_version_id: str, user_id: str, device_id: str, ip: str, totp_secret: str = '', totp_code: str = '') -> Dict[str, Any]:
    """Controller for signing contract. Enforces TOTP on the backend."""
    from utils.permission_utils import can_sign_contract
    from repositories.contract_versions_repo import ContractVersionsRepository as _CVR
    from repositories.contracts_repo import ContractsRepository as _CR
    version = _CVR.get_by_id(contract_version_id)
    if version:
        rows = _CR.get_by_id(version.contract_id)
        if rows and not can_sign_contract(user_id, rows[0]['project_id']):
            return {"status": "error", "message": "Insufficient permissions to sign this contract."}
    return signing_service.sign_contract(contract_version_id, user_id, device_id, ip, totp_secret, totp_code)

def generate_signature_hash(contract_version_id: str, user_id: str) -> str:
    """Controller for generating signature hash."""
    return signing_service.generate_signature_hash(contract_version_id, user_id)

def store_signature(contract_version_id: str, user_id: str, device_id: str, signed_at: str) -> Dict[str, Any]:
    """Controller for storing signature."""
    return signing_service.store_signature(contract_version_id, user_id, device_id, signed_at)

def get_contract_signatures(contract_version_id: str) -> list[Dict[str, Any]]:
    """Controller for getting contract signatures."""
    return signing_service.get_contract_signatures(contract_version_id)

def check_contract_fully_signed(contract_version_id: str, required_user_ids: Set[str]) -> bool:
    """Controller for checking contract fully signed."""
    return signing_service.check_contract_fully_signed(contract_version_id, required_user_ids)

def generate_ephemeral_signing_token(user_id: str, contract_version_id: str) -> Dict[str, Any]:
    """Generate a short-lived signing token bound to the user and document."""
    return signing_service.generate_ephemeral_signing_token(user_id, contract_version_id)
