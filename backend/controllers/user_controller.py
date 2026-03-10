# UserController calls AuthService
from typing import Dict, Any, List, Optional
from services.auth_service import AuthService

auth_service = AuthService()


def signup(email: str, password: str) -> Dict[str, Any]:
    """Sign up a new user. Records consent and accessibility info."""
    return auth_service.create_user(email, password)

def login(email: str, password: str) -> Dict[str, Any]:
    """Authenticate a user with email and password."""
    return auth_service.authenticate_user(email, password)

def verify_totp(user_id: str, totp_secret: str, code: str) -> bool:
    """Verify the user's TOTP authenticator code for 2FA login."""
    return auth_service.verify_totp(user_id, totp_secret, code)

def initiate_password_reset(email: str) -> Dict[str, Any]:
    """Send a password reset link to the user's email."""
    return auth_service.initiate_password_reset(email)

def complete_password_reset(token: str, new_password: str) -> Dict[str, Any]:
    """Complete a password reset using the provided token."""
    return auth_service.complete_password_reset(token, new_password)

def add_device(user_id: str, device_info: str) -> Dict[str, Any]:
    """Register a new device (untrusted until authenticator + email verified)."""
    return auth_service.register_device(user_id, device_info)

def verify_new_device(user_id: str, device_id: str) -> Dict[str, Any]:
    """Mark a newly registered device as trusted after challenge is passed."""
    return auth_service.verify_new_device(user_id, device_id)

def revoke_device(user_id: str, device_id: str) -> Dict[str, Any]:
    """Revoke a device. Triggers breach notification if device is lost/stolen."""
    return auth_service.revoke_device(user_id, device_id)

def get_user_devices(user_id: str) -> List[Dict[str, Any]]:
    """Return all registered devices for a user."""
    return auth_service.get_user_devices(user_id)

def remove_account(user_id: str) -> Dict[str, Any]:
    """Delete a user account. Audit logs and evidence are preserved for legal compliance."""
    return auth_service.remove_account(user_id)

def start_identity_verification(user_id: str) -> Dict[str, Any]:
    """Initiate identity verification for higher legal assurance."""
    return auth_service.start_identity_verification(user_id)

def store_identity_verification_result(user_id: str, provider: str, status: str) -> Dict[str, Any]:
    """Store the result of an identity verification check."""
    return auth_service.store_identity_verification_result(user_id, provider, status)

def check_identity_verification_status(user_id: str) -> Dict[str, Any]:
    """Return the current identity verification status for a user."""
    return auth_service.check_identity_verification_status(user_id)
