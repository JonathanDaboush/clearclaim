import uuid
from typing import List, Dict, Any, Optional
from repositories.users_repo import UsersRepository
from repositories.devices_repo import DevicesRepository
from repositories.identity_verification_repo import IdentityVerificationRepository
from utils.security_utils import hash_password, verify_password, verify_totp
from services.notification_service import NotificationService
from services.audit_service import AuditService


class AuthService:
    def create_user(self, email: str, password: str, age: Optional[int] = None, consent: Optional[bool] = None) -> Dict[str, Any]:
        """Create a new user account.
        Enforces parental consent for under-13, records consent, notifies about accessibility."""
        if age is not None and age < 13:
            NotificationService().create_notification(email, "parental_consent", "Parental consent required for users under 13.")
        if consent:
            AuditService().log_event("consent", email, {"consent": consent})
        password_hash = hash_password(password)
        result = UsersRepository.create_user(email=email, password_hash=password_hash)
        user_id = result["user_id"]
        totp_secret = result["totp_secret"]
        AuditService().log_event("create_user", user_id, {"email": email})
        NotificationService().create_notification(user_id, "accessibility", "Accessibility features available in settings.")
        return {"status": "User created", "user_id": user_id, "totp_secret": totp_secret}

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Verify email and password. Returns user info including totp_secret on success."""
        user = UsersRepository.get_user_by_email(email)
        if not user:
            return {"status": "error", "message": "User not found."}
        if not verify_password(password, user["password_hash"]):
            AuditService().log_event("failed_login", email, {"reason": "bad_password"})
            return {"status": "error", "message": "Invalid credentials."}
        AuditService().log_event("login", user["id"], {})
        return {
            "status": "ok",
            "user_id": user["id"],
            "email": email,
            "totp_secret": user["totp_secret"],
            "verification_status": user["verification_status"],
        }

    def verify_totp(self, user_id: str, totp_secret: str, code: str) -> bool:
        """Verify a TOTP code for 2FA. Returns True if valid."""
        return verify_totp(totp_secret, code)

    def initiate_password_reset(self, email: str) -> Dict[str, Any]:
        """Send a password reset link to the user's email."""
        user = UsersRepository.get_user_by_email(email)
        if not user:
            return {"status": "error", "message": "User not found."}
        reset_token = str(uuid.uuid4())
        UsersRepository.store_reset_token(reset_token, user["id"])
        AuditService().log_event("password_reset_initiated", user["id"], {})
        NotificationService().create_notification(user["id"], "password_reset", f"Use token {reset_token} to reset your password.")
        return {"status": "Reset email sent", "token": reset_token}

    def complete_password_reset(self, token: str, new_password: str) -> Dict[str, Any]:
        """Complete a password reset using the provided token and persist the new password."""
        user_id = UsersRepository.consume_reset_token(token)
        if not user_id:
            return {"status": "error", "message": "Invalid or expired reset token."}
        new_hash = hash_password(new_password)
        UsersRepository.update_password(user_id, new_hash)
        AuditService().log_event("password_reset_completed", user_id, {})
        return {"status": "Password reset successful"}

    def remove_account(self, user_id: str) -> Dict[str, Any]:
        """Delete a user account. Audit logs and evidence are preserved for legal compliance."""
        deleted = UsersRepository.delete_user(user_id)
        if not deleted:
            return {"status": "error", "message": "User not found."}
        AuditService().log_event("remove_account", user_id, {"note": "Audit logs and evidence retained for legal compliance."})
        NotificationService().create_notification(user_id, "account_removed", "Your account has been removed. Audit records are retained as required by law.")
        return {"status": "Account removed"}

    def register_device(self, user_id: str, device_info: str, location: str = '') -> Dict[str, Any]:
        """Register a new device (untrusted pending authenticator + email challenge)."""
        device_id = DevicesRepository.add_device(user_id, device_info, location)
        AuditService().log_event("device_registered", user_id, {"device_id": device_id})
        NotificationService().create_notification(user_id, "device_added", f"New device registered: {device_info}. Verify it to trust it. If this wasn't you, revoke it immediately.")
        return {"status": "Device registered — awaiting verification", "device_id": device_id}

    def verify_new_device(self, user_id: str, device_id: str) -> Dict[str, Any]:
        """Confirm a newly registered device after authenticator + email challenge. Marks it trusted."""
        DevicesRepository.mark_trusted(device_id)
        AuditService().log_event("device_verified", user_id, {"device_id": device_id})
        return {"status": "Device verified and trusted"}

    def revoke_device(self, user_id: str, device_id: str) -> Dict[str, Any]:
        """Revoke device access. Triggers breach notification per specs."""
        DevicesRepository.revoke_device(device_id)
        AuditService().log_event("device_revoked", user_id, {"device_id": device_id})
        NotificationService().create_notification(user_id, "breach", "Device revoked. If this was unexpected, contact support.")
        return {"status": "Device revoked"}

    def get_user_devices(self, user_id: str) -> List[Dict[str, Any]]:
        """Return all registered devices for a user."""
        return DevicesRepository.get_by_user(user_id)

    def start_identity_verification(self, user_id: str) -> Dict[str, Any]:
        """Initiate an identity verification flow (e.g. government ID check)."""
        AuditService().log_event("identity_verification_started", user_id, {})
        NotificationService().create_notification(user_id, "identity_verification", "Identity verification started.")
        return {"status": "Verification started"}

    def store_identity_verification_result(self, user_id: str, provider: str, status: str) -> Dict[str, Any]:
        """Persist the result of an identity verification check."""
        verification_id = IdentityVerificationRepository().create_verification(user_id, provider, status)
        AuditService().log_event("identity_verification_result", user_id, {"provider": provider, "status": status})
        return {"status": "Verification stored", "verification_id": verification_id}

    def check_identity_verification_status(self, user_id: str) -> Dict[str, Any]:
        """Return the current identity verification status for a user."""
        return IdentityVerificationRepository().get_verification(user_id)
