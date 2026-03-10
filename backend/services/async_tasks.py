import threading
from repositories.audit_repo import AuditRepository


class AsyncTasks:
    @staticmethod
    def send_email_async(user_id: str, subject: str, message: str):
        """Fire-and-forget email send (stub: runs in background thread)."""
        def _send():
            # TODO: integrate SMTP / SendGrid
            print(f"[EMAIL] To={user_id} Subject={subject} Message={message}")
        threading.Thread(target=_send, daemon=True).start()

    @staticmethod
    def scan_file_async(file_bytes: bytes, evidence_id: str):
        """Fire-and-forget virus scan (stub: logs the scan request)."""
        def _scan():
            # TODO: integrate ClamAV or cloud AV API
            print(f"[SCAN] evidence_id={evidence_id}")
        threading.Thread(target=_scan, daemon=True).start()

    @staticmethod
    def anchor_audit_snapshot_async(snapshot_hash: str):
        """Fire-and-forget external anchoring of an audit snapshot hash."""
        def _anchor():
            # TODO: write hash to external ledger / archived storage
            print(f"[ANCHOR] snapshot_hash={snapshot_hash}")
        threading.Thread(target=_anchor, daemon=True).start()

    @staticmethod
    def detect_suspicious_activity_async(user_id: str, event_type: str):
        """Fire-and-forget suspicious activity check. Logs a breach event if flagged."""
        def _detect():
            suspicious_events = {"repeated_failed_signing", "new_device_login", "unusual_activity"}
            if event_type in suspicious_events:
                AuditRepository.log_event(
                    user_id=user_id,
                    device_id="",
                    event_type="suspicious_activity",
                    details=f"Flagged event: {event_type}",
                )
        threading.Thread(target=_detect, daemon=True).start()
