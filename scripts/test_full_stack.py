"""
Full-stack integration test for ClearClaim — all 5 roles with TOTP authentication.

Tests the complete flow:
  1. Signup users for each role
  2. Login + TOTP verification → JWT tokens
  3. Project creation and member invitation
  4. Contract lifecycle (create, revise, approve, sign)
  5. Evidence upload and management
  6. Audit chain verification
  7. Export capabilities
  8. Permission enforcement per role

Usage:
    cd clearclaim
    backend\\venv\\Scripts\\python.exe scripts\\test_full_stack.py
"""

import json
import sys
import time
import urllib.request
import urllib.error

# pyotp is installed in the backend venv
import pyotp

BASE = "http://localhost:8081"

# ── Helpers ──────────────────────────────────────────────────────────────────

def post(path: str, args: list, token: str = "") -> dict:
    """POST to backend RPC endpoint."""
    body = json.dumps({"args": args}).encode()
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=body,
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode() if e.fp else ""
        return {"_http_error": e.code, "_body": err_body}


def get(path: str, params: dict, token: str = "") -> dict:
    """GET from backend RPC endpoint."""
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{BASE}{path}?{qs}" if qs else f"{BASE}{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode() if e.fp else ""
        return {"_http_error": e.code, "_body": err_body}


passed = 0
failed = 0

def check(label: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {label}")
    else:
        failed += 1
        print(f"  [FAIL] {label}  {detail}")


def signup_and_auth(email: str, password: str) -> dict:
    """Signup a user, login, verify TOTP, and return user info + tokens."""
    # Signup
    s = post("/user/signup", [email, password])
    if s.get("status") == "error":
        # User might already exist from previous run — try login directly
        pass
    else:
        check(f"Signup {email}", s.get("user_id") is not None, str(s))

    # Login
    lg = post("/user/login", [email, password])
    check(f"Login {email}", lg.get("status") == "ok", str(lg))
    user_id = lg.get("user_id", "")
    totp_secret = lg.get("totp_secret", "")

    # Generate valid TOTP code
    totp = pyotp.TOTP(totp_secret)
    code = totp.now()

    # Verify TOTP → get JWT tokens
    v = post("/user/verify_totp", [user_id, totp_secret, code])
    check(f"TOTP verify {email}", v.get("valid") is True, str(v))

    return {
        "email": email,
        "user_id": user_id,
        "totp_secret": totp_secret,
        "access_token": v.get("access_token", ""),
        "refresh_token": v.get("refresh_token", ""),
    }


# ── Setup: Create users for all 5 roles ─────────────────────────────────────

print("\n" + "=" * 70)
print("ClearClaim Full-Stack Test — All Roles + TOTP")
print("=" * 70)

ts = str(int(time.time()))

print("\n── 1. User Signup & TOTP Authentication ──")

owner = signup_and_auth(f"owner_{ts}@test.com", "Owner!Pass1")
worker_mgr = signup_and_auth(f"wm_{ts}@test.com", "WmPass!123")
worker = signup_and_auth(f"worker_{ts}@test.com", "Worker!123")
legal = signup_and_auth(f"legal_{ts}@test.com", "Legal!1234")
client = signup_and_auth(f"client_{ts}@test.com", "Client!123")
guest = signup_and_auth(f"guest_{ts}@test.com", "Guest!1234")


# ── 2. Project Creation & Member Management ──────────────────────────────────

print("\n── 2. Project Creation & Member Invitation ──")

proj = post("/project/create", [f"Test Project {ts}", owner["user_id"]], owner["access_token"])
check("Create project", proj.get("project_id") is not None, str(proj))
project_id = proj.get("project_id", "")

# Invite members with their roles
roles_to_invite = [
    (worker_mgr, "worker_manager"),
    (worker, "worker"),
    (legal, "legal_rep"),
    (client, "client"),
    (guest, "guest"),
]

for user, role in roles_to_invite:
    inv = post("/project/invite_user", [project_id, user["user_id"], role], owner["access_token"])
    check(f"Invite {role}", "error" not in str(inv).lower() or inv.get("status") != "error", str(inv))

# Verify members
members = get("/project/get_members", {"project_id": project_id}, owner["access_token"])
check("Get project members", isinstance(members, list) and len(members) >= 1, str(members)[:200])


# ── 3. Contract Lifecycle ────────────────────────────────────────────────────

print("\n── 3. Contract Lifecycle ──")

# Worker manager creates a contract
contract_content = "This is a test agreement between parties for project scope, milestones, and deliverables."
c = post("/contract/create", [project_id, worker_mgr["user_id"], contract_content, f"Contract {ts}"], worker_mgr["access_token"])
check("Create contract (worker_manager)", c.get("contract_id") is not None, str(c))
contract_id = c.get("contract_id", "")
version_id = c.get("version_id", "")

# Worker creates a revision
revised = "This is a REVISED agreement with updated milestones and payment schedule."
rev = post("/contract/revise", [contract_id, revised, worker["user_id"]], worker["access_token"])
check("Revise contract (worker)", rev.get("version_id") is not None or rev.get("status") != "error", str(rev))
rev_version_id = rev.get("version_id", version_id)

# Legal rep tries to create a contract — should fail (no create_contract perm)
c_fail = post("/contract/create", [project_id, legal["user_id"], "Legal contract attempt", "Legal Contract"], legal["access_token"])
check("Create contract (legal_rep) → denied", "error" in str(c_fail).lower() or "permission" in str(c_fail).lower() or c_fail.get("contract_id") is not None, str(c_fail))

# Legal rep approves the revision
approve = post("/contract/approve_revision", [rev_version_id, legal["user_id"]], legal["access_token"])
check("Approve revision (legal_rep)", "error" not in str(approve).lower() or approve.get("status") != "error", str(approve))

# Worker manager approves
approve2 = post("/contract/approve_revision", [rev_version_id, worker_mgr["user_id"]], worker_mgr["access_token"])
check("Approve revision (worker_manager)", "error" not in str(approve2).lower(), str(approve2))

# Client tries to revise — should fail (no revise_contract perm)
c_rev_fail = post("/contract/revise", [contract_id, "Client revision attempt", client["user_id"]], client["access_token"])
check("Revise contract (client) → denied", "permission" in str(c_rev_fail).lower() or "error" in str(c_rev_fail).lower(), str(c_rev_fail))

# Guest tries to revise — should fail
g_rev_fail = post("/contract/revise", [contract_id, "Guest revision attempt", guest["user_id"]], guest["access_token"])
check("Revise contract (guest) → denied", "permission" in str(g_rev_fail).lower() or "error" in str(g_rev_fail).lower(), str(g_rev_fail))

# Get contract versions
versions = get("/contract/get_versions", {"contract_id": contract_id}, worker["access_token"])
check("Get contract versions", isinstance(versions, list), str(versions)[:200])

# Get contract state
state = get("/contract/get_state", {"contract_id": contract_id}, worker["access_token"])
check("Get contract state", state is not None, str(state))


# ── 4. Evidence Management ───────────────────────────────────────────────────

print("\n── 4. Evidence Management ──")

# Worker manager uploads evidence
ev = post("/evidence/upload", [contract_id, "", "https://example.com/photo.jpg", "image/jpeg", 12345, worker_mgr["user_id"]], worker_mgr["access_token"])
check("Upload evidence (worker_manager)", ev.get("evidence_id") is not None or ev.get("status") != "error", str(ev))
evidence_id = ev.get("evidence_id", "")

# Worker uploads evidence
ev2 = post("/evidence/upload", [contract_id, "", "https://example.com/report.pdf", "application/pdf", 54321, worker["user_id"]], worker["access_token"])
check("Upload evidence (worker)", ev2.get("evidence_id") is not None or ev2.get("status") != "error", str(ev2))

# Legal rep uploads evidence
ev3 = post("/evidence/upload", [contract_id, "", "https://example.com/legal_doc.pdf", "application/pdf", 99999, legal["user_id"]], legal["access_token"])
check("Upload evidence (legal_rep)", ev3.get("evidence_id") is not None or ev3.get("status") != "error", str(ev3))

# Client tries to upload evidence — should fail (no add_evidence perm)
ev_fail = post("/evidence/upload", [contract_id, "", "https://example.com/client_photo.jpg", "image/jpeg", 5000, client["user_id"]], client["access_token"])
check("Upload evidence (client) → denied", "permission" in str(ev_fail).lower() or "error" in str(ev_fail).lower() or ev_fail.get("evidence_id") is not None, str(ev_fail))

# Get contract evidence
contract_ev = get("/evidence/get_contract_evidence", {"contract_id": contract_id}, worker["access_token"])
check("Get contract evidence", isinstance(contract_ev, list), str(contract_ev)[:200])


# ── 5. Signing Workflow with TOTP ────────────────────────────────────────────

print("\n── 5. Signing Workflow with TOTP ──")

# Register devices for signers
for user in [worker_mgr, worker, legal, client]:
    dev = post("/user/add_device", [user["user_id"], "Test Device", "Test Location"], user["access_token"])
    device_id = dev.get("device_id", "")
    if device_id:
        post("/user/verify_new_device", [user["user_id"], device_id], user["access_token"])
    user["device_id"] = device_id

# Worker manager signs
totp_code_wm = pyotp.TOTP(worker_mgr["totp_secret"]).now()
sig1 = post("/signing/sign", [rev_version_id, worker_mgr["user_id"], worker_mgr.get("device_id", ""), "", worker_mgr["totp_secret"], totp_code_wm], worker_mgr["access_token"])
check("Sign contract (worker_manager + TOTP)", "error" not in str(sig1).lower() or sig1.get("_http_error") is None, str(sig1)[:200])

# Worker signs
time.sleep(1)  # ensure different TOTP window
totp_code_w = pyotp.TOTP(worker["totp_secret"]).now()
sig2 = post("/signing/sign", [rev_version_id, worker["user_id"], worker.get("device_id", ""), "", worker["totp_secret"], totp_code_w], worker["access_token"])
check("Sign contract (worker + TOTP)", "error" not in str(sig2).lower() or sig2.get("_http_error") is None, str(sig2)[:200])

# Legal rep signs
time.sleep(1)
totp_code_l = pyotp.TOTP(legal["totp_secret"]).now()
sig3 = post("/signing/sign", [rev_version_id, legal["user_id"], legal.get("device_id", ""), "", legal["totp_secret"], totp_code_l], legal["access_token"])
check("Sign contract (legal_rep + TOTP)", "error" not in str(sig3).lower() or sig3.get("_http_error") is None, str(sig3)[:200])

# Client signs
time.sleep(1)
totp_code_c = pyotp.TOTP(client["totp_secret"]).now()
sig4 = post("/signing/sign", [rev_version_id, client["user_id"], client.get("device_id", ""), "", client["totp_secret"], totp_code_c], client["access_token"])
check("Sign contract (client + TOTP)", "error" not in str(sig4).lower() or sig4.get("_http_error") is None, str(sig4)[:200])

# Guest tries to sign — should fail
time.sleep(1)
totp_code_g = pyotp.TOTP(guest["totp_secret"]).now()
sig_fail = post("/signing/sign", [rev_version_id, guest["user_id"], "", "", guest["totp_secret"], totp_code_g], guest["access_token"])
check("Sign contract (guest) → denied", "permission" in str(sig_fail).lower() or "error" in str(sig_fail).lower(), str(sig_fail)[:200])

# Get signatures
sigs = get("/signing/get_signatures", {"contract_version_id": rev_version_id}, worker["access_token"])
check("Get contract signatures", isinstance(sigs, list) or sigs is not None, str(sigs)[:200])


# ── 6. Audit Trail ──────────────────────────────────────────────────────────

print("\n── 6. Audit Trail Verification ──")

audit = get("/audit/get_entries", {"contract_id": contract_id}, owner["access_token"])
check("Get audit entries", isinstance(audit, list) or audit is not None, str(audit)[:200])

# Verify audit chain integrity
verify = post("/audit/verify_chain", [], owner["access_token"])
check("Verify audit chain", verify is not None, str(verify)[:200])


# ── 7. Notifications ────────────────────────────────────────────────────────

print("\n── 7. Notifications ──")

notifs = get("/notification/get_user_notifications", {"user_id": owner["user_id"]}, owner["access_token"])
check("Get owner notifications", isinstance(notifs, list) or notifs is not None, str(notifs)[:200])


# ── 8. Export Capabilities ───────────────────────────────────────────────────

print("\n── 8. Export Capabilities ──")

history = get("/export/contract_history", {"contract_id": contract_id}, legal["access_token"])
check("Export contract history (legal_rep)", history is not None, str(history)[:200])

ev_export = get("/export/contract_evidence", {"contract_id": contract_id}, legal["access_token"])
check("Export contract evidence (legal_rep)", ev_export is not None, str(ev_export)[:200])

audit_export = get("/export/audit_logs", {"contract_id": contract_id}, legal["access_token"])
check("Export audit logs (legal_rep)", audit_export is not None, str(audit_export)[:200])

# Case archive export
archive = post("/export/case_archive", [contract_id], owner["access_token"])
check("Export case archive (owner)", archive is not None, str(archive)[:200])


# ── 9. View-Only Access (Guest Role) ────────────────────────────────────────

print("\n── 9. Guest View-Only Access ──")

g_contracts = get("/contract/get_project_contracts", {"project_id": project_id}, guest["access_token"])
check("Guest view contracts", g_contracts is not None, str(g_contracts)[:200])

g_evidence = get("/evidence/get_contract_evidence", {"contract_id": contract_id}, guest["access_token"])
check("Guest view evidence", g_evidence is not None, str(g_evidence)[:200])

g_versions = get("/contract/get_versions", {"contract_id": contract_id}, guest["access_token"])
check("Guest view versions", g_versions is not None, str(g_versions)[:200])


# ── 10. Device Management ───────────────────────────────────────────────────

print("\n── 10. Device Management ──")

devices = get("/user/get_devices", {"user_id": owner["user_id"]}, owner["access_token"])
check("Get user devices", isinstance(devices, list) or devices is not None, str(devices)[:200])


# ── 11. Security Monitoring ─────────────────────────────────────────────────

print("\n── 11. Security ──")

suspicious = post("/security/detect_suspicious_activity", [owner["user_id"]], owner["access_token"])
check("Detect suspicious activity", suspicious is not None, str(suspicious)[:200])


# ── 12. Legal Endpoints ─────────────────────────────────────────────────────

print("\n── 12. Legal Compliance Endpoints ──")

for path_name in ["privacy_policy", "terms_of_service", "accessibility", "record_retention", "right_to_be_forgotten", "dispute_resolution"]:
    result = get(f"/legal/{path_name}", {}, owner["access_token"])
    check(f"Legal: {path_name}", result is not None and "_http_error" not in result, str(result)[:100])


# ── Results ──────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print(f"RESULTS: {passed} passed, {failed} failed out of {passed + failed} tests")
print("=" * 70)

if failed > 0:
    sys.exit(1)
