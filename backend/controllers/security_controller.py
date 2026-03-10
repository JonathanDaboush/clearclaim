# SecurityController calls SecurityService
from typing import Dict, Any
from services.security_service import SecurityService

security_service = SecurityService()


def detect_suspicious_activity(user_id: str, event_type: str) -> Dict[str, Any]:
    """Detect suspicious activity and trigger restrictions and alerts."""
    return security_service.detect_suspicious_activity(user_id, event_type)

def restrict_actions(user_id: str, reason: str) -> Dict[str, Any]:
    """Temporarily restrict a user's sensitive actions."""
    return security_service.restrict_actions(user_id, reason)

def lift_restriction(user_id: str) -> Dict[str, Any]:
    """Lift temporary action restrictions from a user."""
    return security_service.lift_restriction(user_id)

def is_restricted(user_id: str) -> bool:
    """Return True if the user currently has restricted sensitive actions."""
    return security_service.is_restricted(user_id)

def recover_device(user_id: str, new_device_info: str) -> Dict[str, Any]:
    """Initiate device recovery by registering a new device pending identity verification."""
    return security_service.recover_device(user_id, new_device_info)

def send_security_alert(user_id: str, event_type: str, message: str) -> Dict[str, Any]:
    """Send a security alert to the user."""
    return security_service.send_security_alert(user_id, event_type, message)
