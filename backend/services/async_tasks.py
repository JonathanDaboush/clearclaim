"""Async task handlers registered with the persistent background task queue.

Each handler is a plain function that the task queue worker calls with the
payload dict previously stored in the task_queue table.  Any exception causes
the task to be retried (with exponential back-off) up to max_retries times
before landing in the dead-letter 'failed' state.

Legacy API `AsyncTasks.*_async` is preserved so existing call sites keep
working without changes — they now enqueue a persistent task rather than
spinning a raw daemon thread.
"""

from workers.task_queue import task_queue


# ── Handler registration ──────────────────────────────────────────────────────

@task_queue.register("send_email")
def _handle_send_email(user_id: str, subject: str, message: str, notification_id: str = '', **_):
    """Send an email via SMTP. Falls back to console log if SMTP is not configured."""
    import os, smtplib
    from email.mime.text import MIMEText

    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    smtp_from = os.environ.get("SMTP_FROM", smtp_user or "noreply@clearclaim.app")

    # Resolve email address: user_id may be a UUID or already an email
    to_addr = user_id
    if "@" not in user_id:
        try:
            import db as _db
            rows = _db.query("SELECT email FROM users WHERE id = %s", (user_id,))
            if rows:
                to_addr = rows[0]["email"]
            else:
                print(f"[EMAIL] Cannot resolve email for user_id={user_id!r}. Dropping.")
                return
        except Exception as e:
            print(f"[EMAIL] DB lookup failed: {e}. Dropping.")
            return

    if not smtp_host:
        # SMTP not configured — log to console (dev mode)
        print(f"[EMAIL] (SMTP not configured) To={to_addr!r} Subject={subject!r}")
        print(f"[EMAIL] Body: {message}")
        return

    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = smtp_from
    msg["To"] = to_addr
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as smtp:
            smtp.ehlo()
            smtp.starttls()
            if smtp_user:
                smtp.login(smtp_user, smtp_pass)
            smtp.sendmail(smtp_from, to_addr, msg.as_string())
        print(f"[EMAIL] Sent to {to_addr!r} Subject={subject!r}")
    except Exception as exc:
        print(f"[EMAIL] Send failed ({exc!r}) — re-raising for retry")
        raise


@task_queue.register("scan_file")
def _handle_scan_file(evidence_id: str, **_):
    """Run a virus scan on a stored evidence file (stub)."""
    print(f"[SCAN] evidence_id={evidence_id!r}")


@task_queue.register("anchor_audit_snapshot")
def _handle_anchor_audit_snapshot(snapshot_hash: str, **_):
    """Write snapshot hash to an external tamper-evident ledger (stub)."""
    print(f"[ANCHOR] snapshot_hash={snapshot_hash!r}")


@task_queue.register("detect_suspicious_activity")
def _handle_detect_suspicious_activity(user_id: str, event_type: str, **_):
    """Classify the event and insert a suspicious_activity audit entry if warranted."""
    suspicious_events = {"repeated_failed_signing", "new_device_login", "unusual_activity"}
    if event_type in suspicious_events:
        from repositories.audit_repo import AuditRepository
        AuditRepository.log_event(
            user_id=user_id,
            device_id="",
            event_type="suspicious_activity",
            details=f"Flagged event: {event_type}",
        )


@task_queue.register("retry_failed_notifications")
def _handle_retry_failed_notifications(**_):
    """Re-attempt delivery for notifications stuck in 'retrying' state."""
    from services.notification_service import NotificationService
    NotificationService().retry_failed_notifications()


# ── Backwards-compatible shim ─────────────────────────────────────────────────

class AsyncTasks:
    """Facade kept so existing service code doesn't need updating.

    Each *_async method now enqueues a persistent task instead of spawning
    a raw daemon thread.
    """

    @staticmethod
    def send_email_async(user_id: str, subject: str, message: str, notification_id: str = ''):
        task_queue.enqueue("send_email", {
            "user_id": user_id,
            "subject": subject,
            "message": message,
            "notification_id": notification_id,
        })

    @staticmethod
    def scan_file_async(file_bytes: bytes, evidence_id: str):
        # file_bytes cannot be serialised to JSON — only pass the ID;
        # the handler should re-read the file from object storage.
        task_queue.enqueue("scan_file", {"evidence_id": evidence_id})

    @staticmethod
    def anchor_audit_snapshot_async(snapshot_hash: str):
        task_queue.enqueue("anchor_audit_snapshot", {"snapshot_hash": snapshot_hash})

    @staticmethod
    def detect_suspicious_activity_async(user_id: str, event_type: str):
        task_queue.enqueue("detect_suspicious_activity", {
            "user_id": user_id,
            "event_type": event_type,
        })
