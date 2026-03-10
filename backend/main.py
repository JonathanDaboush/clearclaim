# Main wrapper for controllers

from services.auth_service import AuthService
from services.project_service import ProjectService
from services.contract_service import ContractService
from services.signing_service import SigningService
from services.audit_service import AuditService
from services.notification_service import NotificationService
from services.billing_service import BillingService

# Role enum and permission map
ROLE_MANAGER = 'manager'
ROLE_LAWYER = 'lawyer'
ROLE_CLIENT = 'client'
ROLE_GUEST = 'guest'

ROLE_PERMISSIONS = {
    ROLE_MANAGER: ['create_contract', 'revise_contract', 'approve_revision', 'add_evidence'],
    ROLE_LAWYER: ['approve_revision', 'sign_contract'],
    ROLE_CLIENT: ['sign_contract'],
    ROLE_GUEST: ['view']
}

SERVICES = {
    'auth': AuthService(),
    'project': ProjectService(),
    'contract': ContractService(),
    'signing': SigningService(),
    'audit': AuditService(),
    'notification': NotificationService(),
    'billing': BillingService()
}

ROUTES = {
    '/auth/signup': SERVICES['auth'].signup,
    '/auth/login': SERVICES['auth'].login,
    '/auth/add_device': SERVICES['auth'].add_device,
    '/auth/revoke_device': SERVICES['auth'].revoke_device,
    '/auth/verify_device': SERVICES['auth'].verify_device,
    '/auth/verify_identity': SERVICES['auth'].verify_identity,
    '/project/create': SERVICES['project'].create_project,
    '/project/create_subgroup': SERVICES['project'].create_subgroup,
    '/project/add_member': SERVICES['project'].add_member,
    '/project/remove_member': SERVICES['project'].remove_member,
    '/project/get_permissions': SERVICES['project'].get_permissions,
    '/contract/create': SERVICES['contract'].create_contract,
    '/contract/revise': SERVICES['contract'].revise_contract,
    '/contract/approve_revision': SERVICES['contract'].approve_revision,
    '/contract/export': SERVICES['contract'].export_contract,
    '/contract/add_evidence': SERVICES['contract'].add_evidence,
    '/contract/remove_evidence': SERVICES['contract'].remove_evidence,
    '/contract/approve_evidence': SERVICES['contract'].approve_evidence,
    '/signing/sign': SERVICES['signing'].sign_contract,
    '/audit/log': SERVICES['audit'].log_event,
    '/audit/verify_chain': SERVICES['audit'].verify_log_chain,
    '/notification/send': SERVICES['notification'].send_notification,
    '/notification/queue': SERVICES['notification'].queue_notification,
    '/billing/create_subscription': SERVICES['billing'].create_subscription,
    '/billing/cancel_subscription': SERVICES['billing'].cancel_subscription,
    '/billing/record_payment': SERVICES['billing'].record_payment,
}

def route(path, *args, **kwargs):
    """
    Route request to handler based on path.
    Args: path (str), args, kwargs. Returns: handler result.
    """
    handler = ROUTES.get(path)
    if handler:
        return handler(*args, **kwargs)
    else:
        return {'error': 'Path not found'}

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body)
        except Exception:
            data = {}
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        result = route(path, *args, **kwargs)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        args = query.get('args', [])
        kwargs = {k: v[0] for k, v in query.items() if k != 'args'}
        result = route(path, *args, **kwargs)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f'Server running on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
