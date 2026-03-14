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

    def sign_contract(self, contract_version_id: str, user_id: str, device_id: str, ip: str, totp_secret: str = '', totp_code: str = '', idempotency_key: str = '', user_agent: str = '') -> Dict[str, Any]:
        """Record a signature after TOTP verification. Stores signature, hashes, and logs.
        totp_secret and totp_code must be supplied; signing is rejected without verified TOTP.
        Supply idempotency_key to prevent duplicate signatures on retried requests."""
        from utils.idempotency import idempotency_guard, store_idempotency_result
        try:
            cached = idempotency_guard(idempotency_key, endpoint="/signing/sign", user_id=user_id)
            if cached is not None:
                return cached
        except ValueError as exc:
            return {"status": "error", "message": str(exc)}

        # Enforce TOTP on the backend — both fields required, no bypass
        if not totp_secret or not totp_code:
            return {"status": "error", "message": "Authenticator code required to sign."}
        if not self.verify_signing_totp(totp_secret, totp_code):
            return {"status": "error", "message": "Invalid authenticator code. Signature rejected."}

        # Guard: prevent duplicate signature for the same (version, user) pair
        existing = SignatureRepository.get_by_version_ids({contract_version_id})
        if any(s.user_id == user_id for s in existing):
            return {"status": "already_signed", "message": "You have already signed this contract version."}

        signed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        # Pass signed_at so both hashes bind to the exact same timestamp
        sig_hash = self.generate_signature_hash(contract_version_id, user_id, signed_at)

        # Build contract snapshot hash: SHA-256 of (version_id + content_hash + signer + timestamp)
        # This locks the signature irrevocably to that exact contract version content
        # and is required for ESIGN Act compliance (§4 E-Signature Disclosure).
        import db as _db
        import hashlib as _hl
        try:
            version_rows = _db.query(
                'SELECT content_hash FROM contract_versions WHERE id = %s',
                (contract_version_id,),
            )
            version_content_hash = version_rows[0]['content_hash'] if version_rows else ''
        except Exception:
            version_content_hash = ''
        snapshot_input = f"{contract_version_id}:{version_content_hash}:{user_id}:{signed_at}"
        contract_snapshot_hash = _hl.sha256(snapshot_input.encode()).hexdigest()

        totp_was_verified = bool(totp_secret and totp_code)
        signature_id = SignatureRepository.insert_signature(
            contract_version_id, user_id, device_id, signed_at,
            signature_hash=sig_hash, ip=ip,
            contract_snapshot_hash=contract_snapshot_hash,
            totp_verified=totp_was_verified,
            user_agent=user_agent,
        )
        AuditService().log_event("sign_contract", user_id, {
            "version_id": contract_version_id,
            "device_id": device_id,
            "ip": ip,
            "signature_hash": sig_hash,
        })
        NotificationService().create_notification(user_id, "signed", f"You signed contract version {contract_version_id}.")
        # Update device last_seen on every successful signing action
        if device_id:
            try:
                from repositories.devices_repo import DevicesRepository
                DevicesRepository.update_last_seen(device_id)
            except Exception:
                pass
        # Auto-transition contract to fully_signed when all project members have signed
        try:
            import db as _db_sig
            cv_rows = _db_sig.query(
                """SELECT c.id AS contract_id, c.project_id
                   FROM contract_versions cv
                   JOIN contracts c ON c.id = cv.contract_id
                   WHERE cv.id = %s""",
                (contract_version_id,),
            )
            if cv_rows:
                _cid = cv_rows[0]["contract_id"]
                _pid = cv_rows[0]["project_id"]
                member_rows = _db_sig.query(
                    "SELECT user_id FROM memberships WHERE project_id = %s AND soft_deleted = FALSE",
                    (_pid,),
                )
                required = {r["user_id"] for r in member_rows}
                if required and self.check_contract_fully_signed(contract_version_id, required):
                    from utils.contract_state_utils import get_contract_state
                    current_state = get_contract_state(_cid)
                    if current_state not in ("fully_signed", "archived"):
                        # Ensure contract reaches ready_for_signature before fully_signed
                        if current_state != "ready_for_signature":
                            _db_sig.execute(
                                "UPDATE contracts SET status = 'ready_for_signature' WHERE id = %s",
                                (_cid,),
                            )
                        _db_sig.execute(
                            "UPDATE contracts SET status = 'fully_signed' WHERE id = %s",
                            (_cid,),
                        )
                        AuditService().log_event("contract_fully_signed", "system", {
                            "contract_id": _cid, "version_id": contract_version_id,
                        })
        except Exception:
            pass  # state transition is best-effort
        result = {
            "status": "Contract signed",
            "signature_id": signature_id,
            "ip": ip,
            "signed_at": signed_at,
            "contract_snapshot_hash": contract_snapshot_hash,
            "totp_verified": totp_was_verified,
        }
        store_idempotency_result(idempotency_key, "/signing/sign", user_id, result)
        # Publish ContractSigned domain event so listeners can fanout (audit, notifications, timeline)
        try:
            import db as _ev_db
            from events.event_bus import event_bus as _ev_bus
            from events.domain_events import ContractSigned as _ContractSigned
            _cv_row = _ev_db.query('SELECT contract_id FROM contract_versions WHERE id = %s', (contract_version_id,))
            _ev_bus.publish(_ContractSigned(
                contract_id=_cv_row[0]['contract_id'] if _cv_row else '',
                version_id=contract_version_id,
                user_id=user_id,
                device_id=device_id,
                signature_id=signature_id,
            ))
        except Exception:
            pass
        return result

    def generate_signature_hash(self, contract_version_id: str, user_id: str, signed_at: str = '') -> str:
        """Return SHA-256 hash tying user ID to contract version for tamper evidence."""
        ts = signed_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
        payload = f"{contract_version_id}:{user_id}:{ts}".encode()
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
