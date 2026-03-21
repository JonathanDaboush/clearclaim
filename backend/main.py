# Main wrapper for controllers

import json
import os

# Ensure CWD is the backend directory (so relative paths resolve correctly)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load .env.* file for the current ENV (dev / staging / prod).
# This is a no-op if the variables are already injected (e.g. via Docker env_file).
try:
    from dotenv import load_dotenv
    _env_name = os.environ.get("ENV", "development")
    _env_file_map = {
        "development": "../.env.dev",
        "staging":     "../.env.staging",
        "production":  "../.env.prod",
    }
    load_dotenv(_env_file_map.get(_env_name, "../.env.dev"), override=False)
except ImportError:
    pass

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import parse_qs, urlparse


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

import controllers.auth_controller as auth_ctrl
import controllers.user_controller as user_ctrl
import controllers.audit_controller as audit_ctrl
import controllers.billing_controller as billing_ctrl
import controllers.payment_controller as payment_ctrl
import controllers.contract_controller as contract_ctrl
import controllers.evidence_controller as evidence_ctrl
import controllers.export_controller as export_ctrl
import controllers.notification_controller as notification_ctrl
import controllers.project_controller as project_ctrl
import controllers.security_controller as security_ctrl
import controllers.signing_controller as signing_ctrl

from utils.rate_limiter import RateLimiter, RateLimitExceeded
from utils.jwt_utils import require_auth

# Module-level singleton — shared across all request handler instances
_rate_limiter = RateLimiter()

# Role enum and permission map
ROLE_WORKER_MANAGER = 'worker_manager'  # Worker who can also manage/invite other workers
ROLE_WORKER = 'worker'
ROLE_LEGAL_REP = 'legal_rep'
ROLE_CLIENT = 'client'
ROLE_GUEST = 'guest'

ROLE_PERMISSIONS = {
    ROLE_WORKER_MANAGER: ['create_contract', 'revise_contract', 'approve_revision', 'add_evidence', 'delete_evidence', 'sign_contract', 'manage_workers', 'view'],
    ROLE_WORKER:         ['create_contract', 'revise_contract', 'approve_revision', 'add_evidence', 'sign_contract', 'view'],
    ROLE_LEGAL_REP:      ['approve_revision', 'add_evidence', 'sign_contract', 'view'],
    ROLE_CLIENT:         ['approve_revision', 'sign_contract', 'view'],
    ROLE_GUEST:          ['view'],
}

ROUTES: Dict[str, Callable[..., Any]] = {
    # ── User lifecycle ──────────────────────────────────────────────────────────
    '/user/signup': user_ctrl.signup,
    '/user/login': user_ctrl.login,
    '/user/verify_totp': user_ctrl.verify_totp,
    '/user/initiate_password_reset': user_ctrl.initiate_password_reset,
    '/user/complete_password_reset': user_ctrl.complete_password_reset,
    '/user/add_device': user_ctrl.add_device,
    '/user/verify_new_device': user_ctrl.verify_new_device,
    '/user/revoke_device': user_ctrl.revoke_device,
    '/user/get_devices': user_ctrl.get_user_devices,
    '/user/remove_account': user_ctrl.remove_account,
    '/user/start_identity_verification': user_ctrl.start_identity_verification,
    '/user/store_identity_verification_result': user_ctrl.store_identity_verification_result,
    '/user/check_identity_verification_status': user_ctrl.check_identity_verification_status,
    # ── Added: user profile lookup ────────────────────────────────────────────
    '/user/get_me': user_ctrl.get_me,

    # ── Auth (lower-level) ──────────────────────────────────────────────────────
    '/auth/create_user': auth_ctrl.create_user,
    '/auth/authenticate_user': auth_ctrl.authenticate_user,
    '/auth/verify_totp': auth_ctrl.verify_totp,
    '/auth/initiate_password_reset': auth_ctrl.initiate_password_reset,
    '/auth/complete_password_reset': auth_ctrl.complete_password_reset,
    '/auth/register_device': auth_ctrl.register_device,
    '/auth/verify_new_device': auth_ctrl.verify_new_device,
    '/auth/revoke_device': auth_ctrl.revoke_device,
    '/auth/get_user_devices': auth_ctrl.get_user_devices,
    '/auth/start_identity_verification': auth_ctrl.start_identity_verification,
    '/auth/store_identity_verification_result': auth_ctrl.store_identity_verification_result,
    '/auth/check_identity_verification_status': auth_ctrl.check_identity_verification_status,

    # ── Project ─────────────────────────────────────────────────────────────────
    '/project/create': project_ctrl.create_project,
    '/project/create_subgroup': project_ctrl.create_subgroup,
    '/project/invite_user': project_ctrl.invite_user_to_project,
    '/project/approve_membership': project_ctrl.approve_project_membership,
    '/project/reject_membership': project_ctrl.reject_project_membership,
    '/project/leave': project_ctrl.leave_project,
    '/project/change_user_role': project_ctrl.change_user_role,
    '/project/remove_member': project_ctrl.remove_member,
    '/project/get_members': project_ctrl.get_project_members,
    '/project/get_user_role': project_ctrl.get_user_project_role,
    '/project/join_subgroup': project_ctrl.join_subgroup,
    '/project/leave_subgroup': project_ctrl.leave_subgroup,
    # ── Added: user project listing and per-project contract listing ──────────
    '/project/get_user_projects': project_ctrl.get_user_projects,
    '/project/get_contracts': project_ctrl.get_project_contracts,

    # ── Contract ────────────────────────────────────────────────────────────────
    '/contract/create': contract_ctrl.create_contract,
    '/contract/revise': contract_ctrl.create_contract_revision,
    '/contract/generate_diff': contract_ctrl.generate_contract_diff,
    '/contract/approve_revision': contract_ctrl.approve_contract_revision,
    '/contract/reject_revision':  contract_ctrl.reject_contract_revision,
    '/contract/check_unanimous_approval': contract_ctrl.check_revision_unanimous_approval,
    '/contract/activate_version': contract_ctrl.activate_contract_version,
    '/contract/get_state': contract_ctrl.get_contract_state,
    '/contract/transition_state': contract_ctrl.transition_contract_state,
    '/contract/get_versions': contract_ctrl.get_contract_versions,
    # ── Added: single contract lookup and project-contract listing ────────────
    '/contract/get': contract_ctrl.get_contract,
    '/contract/get_project_contracts': contract_ctrl.get_project_contracts,
    # ── Evidence ────────────────────────────────────────────────────────────────
    '/evidence/upload': evidence_ctrl.upload_evidence,
    '/evidence/validate_file': evidence_ctrl.validate_evidence_file,
    '/evidence/calculate_hash': evidence_ctrl.calculate_evidence_hash,
    '/evidence/store_file': evidence_ctrl.store_evidence_file,
    '/evidence/propose_addition': evidence_ctrl.propose_evidence_addition,
    '/evidence/approve': evidence_ctrl.approve_evidence,
    '/evidence/check_unanimous_approval': evidence_ctrl.check_evidence_unanimous_approval,
    '/evidence/activate': evidence_ctrl.activate_evidence,
    '/evidence/request_deletion': evidence_ctrl.request_evidence_deletion,
    '/evidence/approve_deletion': evidence_ctrl.approve_evidence_deletion,
    '/evidence/delete': evidence_ctrl.delete_evidence,
    '/evidence/get_contract_evidence': evidence_ctrl.get_contract_evidence,
    '/evidence/get_user_evidence': evidence_ctrl.get_user_evidence,

    # ── Signing ─────────────────────────────────────────────────────────────────
    '/signing/request': signing_ctrl.request_signature,
    '/signing/verify_totp': signing_ctrl.verify_signing_totp,
    '/signing/sign': signing_ctrl.sign_contract,
    '/signing/generate_hash': signing_ctrl.generate_signature_hash,
    '/signing/store': signing_ctrl.store_signature,
    '/signing/get_signatures': signing_ctrl.get_contract_signatures,
    '/signing/check_fully_signed': signing_ctrl.check_contract_fully_signed,
    '/signing/ephemeral_token': signing_ctrl.generate_ephemeral_signing_token,

    # ── Audit ───────────────────────────────────────────────────────────────────
    '/audit/log': audit_ctrl.log_event,
    '/audit/get_previous_hash': audit_ctrl.get_previous_log_hash,
    '/audit/generate_hash': audit_ctrl.generate_log_hash,
    '/audit/append': audit_ctrl.append_audit_log,
    '/audit/verify_chain': audit_ctrl.verify_audit_chain,
    '/audit/verify_entries': audit_ctrl.verify_audit_entries,
    '/audit/recalculate_hash': audit_ctrl.recalculate_log_hash,
    '/audit/snapshot': audit_ctrl.generate_audit_snapshot,
    '/audit/archive_snapshot': audit_ctrl.archive_audit_snapshot,
    # ── Added: audit entry retrieval ──────────────────────────────────────────
    '/audit/get_entries': audit_ctrl.get_audit_entries,

    # ── Notification ────────────────────────────────────────────────────────────
    '/notification/send': notification_ctrl.handle_send_notification,
    '/notification/create': notification_ctrl.create_notification,
    '/notification/resolve_recipients': notification_ctrl.resolve_notification_recipients,
    '/notification/send_email': notification_ctrl.send_email_notification,
    '/notification/send_in_app': notification_ctrl.send_in_app_notification,
    '/notification/mark_read': notification_ctrl.mark_notification_read,
    '/notification/get_user_notifications': notification_ctrl.get_user_notifications,

    # ── Billing ─────────────────────────────────────────────────────────────────
    '/billing/create_subscription': billing_ctrl.create_subscription,
    '/billing/cancel_subscription': billing_ctrl.cancel_subscription,
    '/billing/update_subscription_status': billing_ctrl.update_subscription_status,
    '/billing/record_payment': billing_ctrl.record_payment,
    '/billing/get_payment_history': billing_ctrl.get_payment_history,
    '/billing/generate_metrics': billing_ctrl.generate_billing_metrics,

    # ── Payment (alias for billing) ─────────────────────────────────────────────
    '/payment/create_subscription': payment_ctrl.create_subscription,
    '/payment/cancel_subscription': payment_ctrl.cancel_subscription,
    '/payment/update_subscription_status': payment_ctrl.update_subscription_status,
    '/payment/record_payment': payment_ctrl.record_payment,
    '/payment/get_payment_history': payment_ctrl.get_payment_history,
    '/payment/generate_metrics': payment_ctrl.generate_billing_metrics,

    # ── Export ──────────────────────────────────────────────────────────────────
    '/export/contract_history': export_ctrl.export_contract_history,
    '/export/contract_versions': export_ctrl.export_contract_versions,
    '/export/contract_signatures': export_ctrl.export_contract_signatures,
    '/export/contract_evidence': export_ctrl.export_contract_evidence,
    '/export/audit_logs': export_ctrl.export_audit_logs,
    '/export/case_archive': export_ctrl.build_case_archive,

    # ── Security ────────────────────────────────────────────────────────────────
    '/security/detect_suspicious_activity': security_ctrl.detect_suspicious_activity,
    '/security/restrict_actions': security_ctrl.restrict_actions,
    '/security/lift_restriction': security_ctrl.lift_restriction,
    '/security/is_restricted': security_ctrl.is_restricted,
    '/security/recover_device': security_ctrl.recover_device,
    '/security/send_alert': security_ctrl.send_security_alert,

    # ── Legal ────────────────────────────────────────────────────────────────────
    '/legal/privacy_policy': lambda *_a: {'privacy_policy': 'ClearClaim Privacy Policy: We protect your data, comply with PIPEDA, HIPAA, and do not share personal info except as required by law.'},
    '/legal/terms_of_service': lambda *_a: {'terms_of_service': 'ClearClaim Terms of Service: By using this app, you agree to our terms, dispute resolution, and governing law.'},
    '/legal/accessibility': lambda *_a: {'accessibility_statement': 'ClearClaim Accessibility: We support screen readers, keyboard navigation, high-contrast mode. Contact support@clearclaim.com for accessibility issues.'},
    '/legal/breach_notification': lambda *_a: {'breach_notification': 'In case of a data breach, users and authorities will be notified as required by law.'},
    '/legal/consent': lambda *_a: {'consent_management': 'Users can opt-in/opt-out of marketing and non-essential data collection. Consent is recorded and managed.'},
    '/legal/record_retention': lambda *_a: {'record_retention': 'Records are retained as required by law. Audit logs and evidence are immutable and not deleted upon account removal.'},
    '/legal/children_privacy': lambda *_a: {'children_privacy': 'If users under 13 are allowed, parental consent and special protections are implemented.'},
    '/legal/data_localization': lambda *_a: {'data_localization': 'If data is stored outside Canada, users are informed and PIPEDA compliance ensured.'},
    '/legal/dispute_resolution': lambda *_a: {'dispute_resolution': 'Disputes are resolved according to the governing law specified in our terms.'},
    '/legal/right_to_be_forgotten': lambda *_a: {'right_to_be_forgotten': 'Users may request deletion of personal data, but audit logs and evidence are not deleted to preserve legal integrity.'},

    # ── Auth token management ────────────────────────────────────────────────
    '/auth/refresh':  auth_ctrl.refresh_token,
    '/auth/sign_out': auth_ctrl.sign_out,
}

def route(path: str, *args: Any, **kwargs: Any) -> Any:
    """Route a request to the appropriate controller function by path."""
    handler: Callable[..., Any] | None = ROUTES.get(path)
    if handler is not None:
        return handler(*args, **kwargs)
    return {'error': 'Path not found'}


class RequestHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self) -> None:
        """Send CORS headers allowing browser access from any origin."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def do_OPTIONS(self) -> None:
        """Handle preflight CORS requests."""
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self) -> None:
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        client_ip = self.client_address[0]

        # ── JWT authentication ───────────────────────────────────────────────
        auth_header: str = self.headers.get('Authorization', '') or ''
        token_user_id = require_auth(path, auth_header)
        if token_user_id is None:
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'unauthorized',
                'message': 'Valid Bearer token required. Please log in.',
            }).encode())
            return

        # ── Rate limiting ────────────────────────────────────────────────────
        try:
            _rate_limiter.check(client_ip, path)
        except RateLimitExceeded as exc:
            self.send_response(429)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.send_header('Retry-After', str(exc.window))
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "rate_limit_exceeded",
                "message": str(exc),
                "retry_after": exc.window,
            }).encode('utf-8'))
            return

        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data: Dict[str, Any] = json.loads(body)
        except Exception:
            data = {}
        req_args: List[Any] = data.get('args', [])
        req_kwargs: Dict[str, Any] = data.get('kwargs', {})
        # Inject the real client IP for the signing route (3rd positional arg is device_id, 4th is ip)
        if path == '/signing/sign':
            if len(req_args) >= 4:
                req_args[3] = client_ip
            else:
                while len(req_args) < 3:
                    req_args.append('')
                if len(req_args) == 3:
                    req_args.append(client_ip)
        try:
            result = route(path, *req_args, **req_kwargs)
        except Exception as exc:
            import traceback, sys
            traceback.print_exc(file=sys.stderr)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(exc)}).encode('utf-8'))
            return
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def do_GET(self) -> None:
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        req_args: List[str] = query.get('args', [])
        req_kwargs: Dict[str, str] = {k: v[0] for k, v in query.items() if k != 'args'}

        # ── JWT authentication ───────────────────────────────────────────────
        auth_header: str = self.headers.get('Authorization', '') or ''
        token_user_id = require_auth(path, auth_header)
        if token_user_id is None:
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'unauthorized', 'message': 'Valid Bearer token required.'}).encode())
            return

        # ── Signing certificate PDF download ─────────────────────────────────
        if path == '/export/signing_certificate_pdf':
            signature_id = req_kwargs.get('signature_id') or (req_args[0] if req_args else None)
            if not signature_id:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'signature_id required'}).encode())
                return
            try:
                from repositories.signature_repo import SignatureRepository
                from services.pdf_service import generate_signing_certificate
                sigs = SignatureRepository.get_by_version_ids({signature_id})
                sig_data = vars(sigs[0]) if sigs else {'signature_id': signature_id}
                pdf_bytes = generate_signing_certificate(sig_data)
            except Exception as exc:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(exc)}).encode())
                return
            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Disposition', f'attachment; filename="signing-certificate-{signature_id[:8]}.pdf"')
            self.send_header('Content-Length', str(len(pdf_bytes)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(pdf_bytes)
            return

        # ── Timeline PDF download ─────────────────────────────────────────────
        if path == '/export/timeline_pdf':
            contract_id = req_kwargs.get('contract_id') or (req_args[0] if req_args else None)
            try:
                from repositories.audit_repo import AuditRepository
                from services.pdf_service import generate_timeline_pdf
                chain = AuditRepository.get_chain()
                events = [vars(e) for e in chain if not contract_id or e.related_object_id == contract_id]
                title = f"Audit Timeline" + (f" — {contract_id[:8]}" if contract_id else "")
                pdf_bytes = generate_timeline_pdf(events, title)
            except Exception as exc:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(exc)}).encode())
                return
            fname = f"timeline-{contract_id[:8] if contract_id else 'full'}.pdf"
            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Disposition', f'attachment; filename="{fname}"')
            self.send_header('Content-Length', str(len(pdf_bytes)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(pdf_bytes)
            return

        # ── ZIP case-archive download ─────────────────────────────────────────
        if path == '/export/case_archive_zip':
            contract_id = req_kwargs.get('contract_id') or (req_args[0] if req_args else None)
            if not contract_id:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'contract_id required'}).encode())
                return
            try:
                zip_bytes = export_ctrl.build_case_archive_zip(contract_id)
            except Exception as exc:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(exc)}).encode())
                return
            filename = f"case_archive_{contract_id}.zip"
            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Content-Length', str(len(zip_bytes)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(zip_bytes)
            return

        try:
            result = route(path, *req_args, **req_kwargs)
        except Exception as exc:
            import traceback, sys
            traceback.print_exc(file=sys.stderr)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(exc)}).encode('utf-8'))
            return
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        """Log to stderr so we can debug."""
        import sys
        sys.stderr.write("%s - - [%s] %s\n" %
                         (self.client_address[0],
                          self.log_date_time_string(),
                          format%args))


def run_server(port: int = int(os.environ.get("PORT", "8080"))) -> None:
    # ── Error monitoring (Sentry) ─────────────────────────────────────────────
    _sentry_dsn = os.environ.get("SENTRY_DSN", "")
    if _sentry_dsn:
        try:
            import sentry_sdk
            sentry_sdk.init(
                dsn=_sentry_dsn,
                environment=os.environ.get("ENV", "development"),
                # Capture 100% of errors; adjust traces_sample_rate for performance tracing
                traces_sample_rate=0.1,
            )
            print("[sentry] Error monitoring enabled.")
        except ImportError:
            print("[sentry] sentry-sdk not installed — skipping error monitoring.")

    import db as _db
    try:
        _db.init_schema()
    except Exception as exc:
        print(f"[db] Schema init warning: {exc}")
    # Start persistent background workers (email, file-scan, audit anchoring, etc.)
    from workers.task_queue import task_queue
    import services.async_tasks  # noqa: F401 — registers all task handlers as side-effect
    import events.domain_events   # noqa: F401 — registers all event listeners as side-effect
    task_queue.start_workers()
    server_address = ('', port)
    httpd = ThreadedHTTPServer(server_address, RequestHandler)
    print(f'Server running on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
