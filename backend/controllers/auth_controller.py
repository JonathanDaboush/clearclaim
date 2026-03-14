# AuthController calls AuthService
from typing import Dict, Any, List
from services.auth_service import AuthService

auth_service = AuthService()


def create_user(email: str, password: str) -> Dict[str, Any]:
    """Controller for creating user."""
    return auth_service.create_user(email, password)

def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    """Controller for authenticating user."""
    return auth_service.authenticate_user(email, password)

def verify_totp(user_id: str, totp_secret: str, code: str) -> Dict[str, Any]:
    """Verify TOTP and return JWT tokens on success."""
    return auth_service.verify_totp(user_id, totp_secret, code)

def refresh_token(refresh_token: str) -> Dict[str, Any]:
    """Issue a new access token from a valid refresh token."""
    from utils.jwt_utils import refresh_access_token
    result = refresh_access_token(refresh_token)
    if not result:
        return {"error": "invalid_token", "message": "Refresh token is invalid or expired. Please log in again."}
    return result

def sign_out(refresh_token: str) -> Dict[str, Any]:
    """Revoke the given refresh token (sign-out)."""
    from utils.jwt_utils import revoke_refresh_token
    revoke_refresh_token(refresh_token)
    return {"status": "Signed out"}

def initiate_password_reset(email: str) -> Dict[str, Any]:
    return auth_service.initiate_password_reset(email)

def complete_password_reset(token: str, new_password: str) -> Dict[str, Any]:
    return auth_service.complete_password_reset(token, new_password)

def register_device(user_id: str, device_info: str, location: str = '') -> Dict[str, Any]:
    return auth_service.register_device(user_id, device_info, location)

def verify_new_device(user_id: str, device_id: str) -> Dict[str, Any]:
    return auth_service.verify_new_device(user_id, device_id)

def revoke_device(user_id: str, device_id: str) -> Dict[str, Any]:
    return auth_service.revoke_device(user_id, device_id)

def get_user_devices(user_id: str) -> List[Dict[str, Any]]:
    return auth_service.get_user_devices(user_id)

def start_identity_verification(user_id: str) -> Dict[str, Any]:
    return auth_service.start_identity_verification(user_id)

def store_identity_verification_result(user_id: str, provider: str, status: str) -> Dict[str, Any]:
    return auth_service.store_identity_verification_result(user_id, provider, status)

def check_identity_verification_status(user_id: str) -> Dict[str, Any]:
    return auth_service.check_identity_verification_status(user_id)

def remove_account(user_id: str) -> Dict[str, Any]:
    return auth_service.remove_account(user_id)

def add_device(user_id: str, device_info: str, location: str = '') -> Dict[str, Any]:
    return auth_service.register_device(user_id, device_info, location)
