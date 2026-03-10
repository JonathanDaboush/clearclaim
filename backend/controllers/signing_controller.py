# SigningController handler function
    """
    Handler for signing contract.
    Args: contract_version_id, user_id, device_id. Returns: dict result.
    """
    pass
# SigningController calls SigningService
from services.signing_service import SigningService

signing_service = SigningService()

def request_signature(contract_version_id, user_id):
    """Controller for requesting signature."""
    return signing_service.request_signature(contract_version_id, user_id)

def verify_signing_totp(user_id, code):
    """Controller for verifying signing TOTP."""
    return signing_service.verify_signing_totp(user_id, code)

def sign_contract(contract_version_id, user_id, device_id, ip):
    """Controller for signing contract."""
    return signing_service.sign_contract(contract_version_id, user_id, device_id, ip)

def generate_signature_hash(contract_version_id, user_id):
    """Controller for generating signature hash."""
    return signing_service.generate_signature_hash(contract_version_id, user_id)

def store_signature(contract_version_id, user_id, device_id, ip):
    """Controller for storing signature."""
    return signing_service.store_signature(contract_version_id, user_id, device_id, ip)

def get_contract_signatures(contract_version_id):
    """Controller for getting contract signatures."""
    return signing_service.get_contract_signatures(contract_version_id)

def check_contract_fully_signed(contract_version_id):
    """Controller for checking contract fully signed."""
    return signing_service.check_contract_fully_signed(contract_version_id)
