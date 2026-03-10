from typing import Dict, Any
from repositories.devices_repo import DevicesRepository
from services.audit_service import AuditService
from services.notification_service import NotificationService
from services.async_tasks import AsyncTasks


# In-memory store for temporarily restricted users (replace with DB in production)
_restricted_users: Dict[str, str] = {}  # user_id -> reason


class SecurityService:
    def detect_suspicious_activity(self, user_id: str, event_type: str) -> Dict[str, Any]:
        """Detect and flag suspicious activity per specs.
        Suspicious events: new_device_login, unusual_activity, repeated_failed_signing.
        Flags the event, alerts the user, and temporarily restricts sensitive actions."""
        suspicious_events = {"repeated_failed_signing", "new_device_login", "unusual_activity"}
        if event_type not in suspicious_events:
            return {"status": "ok", "flagged": False}
        AuditService().log_event("suspicious_activity", user_id, {"event_type": event_type})
        NotificationService().create_notification(
            user_id,
            "suspicious_activity",
            f"Suspicious activity detected: {event_type}. Sensitive actions temporarily restricted. Contact support if this wasn't you.",
        )
        _restricted_users[user_id] = event_type
        AsyncTasks.detect_suspicious_activity_async(user_id, event_type)
        return {"status": "Suspicious activity flagged", "restricted": True, "event_type": event_type}

    def restrict_actions(self, user_id: str, reason: str) -> Dict[str, Any]:
        """Temporarily restrict a user's sensitive actions (signing, device changes)."""
        _restricted_users[user_id] = reason
        AuditService().log_event("actions_restricted", user_id, {"reason": reason})
        NotificationService().create_notification(
            user_id,
            "actions_restricted",
            f"Your account sensitive actions have been temporarily restricted: {reason}.",
        )
        return {"status": "Actions restricted", "user_id": user_id, "reason": reason}

    def lift_restriction(self, user_id: str) -> Dict[str, Any]:
        """Remove temporary action restrictions from a user."""
        _restricted_users.pop(user_id, None)
        AuditService().log_event("restriction_lifted", user_id, {})
        NotificationService().create_notification(user_id, "restriction_lifted", "Your account restrictions have been lifted.")
        return {"status": "Restrictions lifted", "user_id": user_id}

    def is_restricted(self, user_id: str) -> bool:
        """Return True if the user currently has restricted sensitive actions."""
        return user_id in _restricted_users

    def recover_device(self, user_id: str, new_device_info: str) -> Dict[str, Any]:
        """Support device recovery: register a new trusted device after identity verification.
        Per specs: lost device recovery without breaking log integrity."""
        device_id = DevicesRepository.add_device(user_id, new_device_info)
        # Identity re-verification required before marking trusted
        AuditService().log_event("device_recovery_initiated", user_id, {"new_device_id": device_id})
        NotificationService().create_notification(
            user_id,
            "device_recovery",
            f"A recovery device has been registered ({new_device_info}). Complete identity verification to trust it.",
        )
        return {
            "status": "Recovery device registered — complete identity verification to trust it",
            "device_id": device_id,
        }

    def send_security_alert(self, user_id: str, event_type: str, message: str) -> Dict[str, Any]:
        """Send a security alert to the user and log it."""
        AuditService().log_event("security_alert", user_id, {"event_type": event_type, "message": message})
        NotificationService().create_notification(user_id, event_type, message)
        return {"status": "Alert sent", "user_id": user_id, "event_type": event_type}
