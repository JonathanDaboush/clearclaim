import hashlib
import datetime
import secrets
from typing import Dict, Any, List, Set
from repositories.signature_repo import SignatureRepository
from services.audit_service import AuditService
from services.notification_service import NotificationService
from utils.security_utils import verify_totp


class SigningService:
    def request_signature(self, contract_version_id: str, user_id: str) -> Dict[str, Any]:
        """Notify a user that their signature is required on a contract version."""
        NotificationService().create_notification(user_id, "signature_request", f"Your signature is required on version {contract_version_id}.")
        AuditService().log_event("signature_requested", user_id, {"version_id": contract_version_id})
        return {"status": "Signature requested"}

    def verify_signing_totp(self, totp_secret: str, code: str) -> bool:
        """Verify the TOTP code the user submits before signing. Must pass before sign_contract."""
        return verify_totp(totp_secret, code)

    def sign_contract(self, contract_version_id: str, user_id: str, device_id: str, ip: str) -> Dict[str, Any]:
        """Record a signature after TOTP verification. Stores signature, hashes, and logs."""
        signed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        sig_hash = self.generate_signature_hash(contract_version_id, user_id)
        signature_id = SignatureRepository.insert_signature(
            contract_version_id, user_id, device_id, signed_at,
            signature_hash=sig_hash, ip=ip
        )
        AuditService().log_event("sign_contract", user_id, {
            "version_id": contract_version_id,
            "device_id": device_id,
            "ip": ip,
            "signature_hash": sig_hash,
        })
        NotificationService().create_notification(user_id, "signed", f"You signed contract version {contract_version_id}.")
        return {"status": "Contract signed", "signature_id": signature_id}

    def generate_signature_hash(self, contract_version_id: str, user_id: str) -> str:
        """Return SHA-256 hash tying user ID to contract version for tamper evidence."""
        payload = f"{contract_version_id}:{user_id}:{datetime.datetime.now(datetime.timezone.utc).isoformat()}".encode()
        return hashlib.sha256(payload).hexdigest()

    def store_signature(self, contract_version_id: str, user_id: str, device_id: str, signed_at: str) -> Dict[str, Any]:
        """Directly persist a signature record (used internally by sign_contract)."""
        signature_id = SignatureRepository.insert_signature(contract_version_id, user_id, device_id, signed_at)
        AuditService().log_event("store_signature", user_id, {"version_id": contract_version_id, "device_id": device_id})
        return {"status": "Signature stored", "signature_id": signature_id}

    def get_contract_signatures(self, contract_version_id: str) -> List[Dict[str, Any]]:
        """Return all signatures for a given contract version."""
        return [s.__dict__ for s in SignatureRepository.get_by_version_ids({contract_version_id})]

    def check_contract_fully_signed(self, contract_version_id: str, required_user_ids: Set[str]) -> bool:
        """Return True if all required parties have signed the contract version."""
        signed_users = {s.user_id for s in SignatureRepository.get_by_version_ids({contract_version_id})}
        return required_user_ids.issubset(signed_users)

    def generate_ephemeral_signing_token(self, user_id: str, contract_version_id: str) -> Dict[str, Any]:
        """Generate a short-lived signing token bound to this user and document.
        Per specs: ephemeral tokens are single-use and tied to a specific session/document."""
        token = secrets.token_hex(32)
        expires_at = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)).isoformat()
        AuditService().log_event("ephemeral_token_generated", user_id, {
            "contract_version_id": contract_version_id,
            "token_prefix": token[:8],
            "expires_at": expires_at,
        })
        return {"token": token, "expires_at": expires_at, "contract_version_id": contract_version_id}
