# AuthController calls AuthService
from typing import Dict, Any, List
from services.auth_service import AuthService

auth_service = AuthService()

def create_user(email: str, password: str) -> Dict[str, Any]:
    """Controller for creating user.
    Records user consent, checks children privacy, provides accessibility info."""
    return auth_service.create_user(email, password)

def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    """Controller for authenticating user."""
    return auth_service.authenticate_user(email, password)

def verify_totp(user_id: str, totp_secret: str, code: str) -> bool:
    """Controller for verifying TOTP."""
    return auth_service.verify_totp(user_id, totp_secret, code)

def initiate_password_reset(email: str) -> Dict[str, Any]:
    """Controller for initiating password reset."""
    return auth_service.initiate_password_reset(email)

def complete_password_reset(token: str, new_password: str) -> Dict[str, Any]:
    """Controller for completing password reset."""
    return auth_service.complete_password_reset(token, new_password)

def register_device(user_id: str, device_info: str, location: str = '') -> Dict[str, Any]:
    """Controller for registering device."""
    return auth_service.register_device(user_id, device_info, location)

def verify_new_device(user_id: str, device_id: str) -> Dict[str, Any]:
    """Controller for verifying new device."""
    return auth_service.verify_new_device(user_id, device_id)

def revoke_device(user_id: str, device_id: str) -> Dict[str, Any]:
    """Controller for revoking device.
    Triggers breach notification if device is lost/stolen."""
    return auth_service.revoke_device(user_id, device_id)

def get_user_devices(user_id: str) -> List[Dict[str, Any]]:
    """Controller for getting user devices."""
    return auth_service.get_user_devices(user_id)

def start_identity_verification(user_id: str) -> Dict[str, Any]:
    """Controller for starting identity verification."""
    return auth_service.start_identity_verification(user_id)

def store_identity_verification_result(user_id: str, provider: str, status: str) -> Dict[str, Any]:
    """Controller for storing identity verification result."""
    return auth_service.store_identity_verification_result(user_id, provider, status)

def check_identity_verification_status(user_id: str) -> Dict[str, Any]:
    """Controller for checking identity verification status."""
    return auth_service.check_identity_verification_status(user_id)
