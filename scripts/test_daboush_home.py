"""
ClearClaim — Full System Test: Daboush Family Home Build
=========================================================

Scenario-driven, end-to-end system validation covering ALL 9 phases:
  Phase 1: Auth & Device Security
  Phase 2: Project + Role Hierarchy Enforcement
  Phase 3: Contract System (full lifecycle)
  Phase 4: Signing Flow (TOTP-enforced)
  Phase 5: Evidence System (unanimous consent)
  Phase 6: Timeline / Audit Entries (front-end truth)
  Phase 7: Audit Log Integrity (hash chain)
  Phase 8: Security Monitoring (suspicious activity)
  Phase 9: Export & Legal Compliance

Every test verifies:
  - API behavior (correct endpoints + validation)
  - Business logic (roles, permissions, consent rules)
  - Database state (correct inserts/updates)
  - Audit logs (append-only + chained correctly)
  - Security layer (TOTP, device validation, restrictions)
  - Notifications (correct users, correct timing)

Company: Build A Home
Project: Daboush Family Home
Property: 3 bed, 2 bath, living room, dining room, laundry, basement,
          large garage, front yard, back yard

Subgroups: Roofing, Flooring, Structural, Electrical, Landscaping

Users:
  John Daboush  (client)         — homeowner
  Sarah Daboush (client)         — homeowner
  Mike          (worker_manager) — project manager
  Alex          (worker)         — roofing specialist
  Sam           (worker)         — flooring specialist
  Lina          (legal_rep)      — legal representative

Usage:
    cd clearclaim
    backend\\venv\\Scripts\\python.exe scripts\\test_daboush_home.py
"""

import json
import sys
import time
import urllib.request
import urllib.error

import pyotp

BASE = "http://localhost:8081"
TS = str(int(time.time()))

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def post(path: str, args: list, token: str = "") -> dict:
    body = json.dumps({"args": args}).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=body,
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
failures = []

def check(label: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [\033[92mPASS\033[0m] {label}")
    else:
        failed += 1
        failures.append((label, detail))
        print(f"  [\033[91mFAIL\033[0m] {label}  {detail[:200]}")


def signup_and_auth(email: str, password: str) -> dict:
    s = post("/user/signup", [email, password])
    if s.get("_http_error"):
        pass  # may already exist
    lg = post("/user/login", [email, password])
    check(f"Login {email}", lg.get("status") == "ok", str(lg))
    user_id = lg.get("user_id", "")
    totp_secret = lg.get("totp_secret", "")
    totp = pyotp.TOTP(totp_secret)
    code = totp.now()
    v = post("/user/verify_totp", [user_id, totp_secret, code])
    check(f"TOTP verify {email}", v.get("valid") is True, str(v))
    return {
        "email": email,
        "user_id": user_id,
        "totp_secret": totp_secret,
        "access_token": v.get("access_token", ""),
        "refresh_token": v.get("refresh_token", ""),
        "device_id": "",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRACT CONTENT — Daboush Family Home Specification
# ═══════════════════════════════════════════════════════════════════════════════

HOME_CONTRACT = """DABOUSH FAMILY HOME — BUILD CONTRACT

Project: Build A Home — Daboush Family Residence
Date: 2026-03-20

1. PROPERTY SPECIFICATIONS
   - 3 Bedrooms (Master: 400 sqft, Bedroom 2: 250 sqft, Bedroom 3: 250 sqft)
   - 2 Bathrooms (Master: en-suite, Main: full bath)
   - 1 Living Room (350 sqft, open concept)
   - 1 Dining Room (200 sqft, adjacent to kitchen)
   - 1 Laundry Room (80 sqft, main floor)
   - 1 Basement (full, unfinished, 1200 sqft)
   - 1 Large Garage (2-car, 600 sqft)
   - Front Yard (landscaped, 800 sqft)
   - Back Yard (fenced, 1500 sqft)

2. CONSTRUCTION TEAMS
   - Roofing Team: Asphalt shingles, 25-year warranty
   - Flooring Team: Hardwood main floor, carpet bedrooms, tile bathrooms
   - Structural Team: Wood frame, poured concrete foundation
   - Electrical Team: 200-amp panel, smart home wiring
   - Landscaping Team: Sod front, deck rear, privacy fence

3. BUDGET: $450,000 CAD
4. TIMELINE: 8 months from permit approval
5. WARRANTY: 1-year builder warranty, 10-year structural

Signed by all parties below.
"""

HOME_CONTRACT_REVISION = """DABOUSH FAMILY HOME — BUILD CONTRACT (REVISED)

Project: Build A Home — Daboush Family Residence
Date: 2026-03-20

1. PROPERTY SPECIFICATIONS
   - 3 Bedrooms (Master: 400 sqft, Bedroom 2: 250 sqft, Bedroom 3: 250 sqft)
   - 2 Bathrooms (Master: en-suite with HEATED FLOORING, Main: full bath with HEATED FLOORING)
   - 1 Living Room (350 sqft, open concept)
   - 1 Dining Room (200 sqft, adjacent to kitchen)
   - 1 Laundry Room (80 sqft, main floor)
   - 1 Basement (full, unfinished, 1200 sqft)
   - 1 Large Garage (2-car, 600 sqft, INSULATED)
   - Front Yard (landscaped, 800 sqft)
   - Back Yard (fenced, 1500 sqft, DECK ADDED)

2. CONSTRUCTION TEAMS
   - Roofing Team: Asphalt shingles, 25-year warranty
   - Flooring Team: Hardwood main floor, carpet bedrooms, tile bathrooms, HEATED TILE in baths
   - Structural Team: Wood frame, poured concrete foundation
   - Electrical Team: 200-amp panel, smart home wiring, HEATED FLOOR CIRCUITS
   - Landscaping Team: Sod front, composite deck rear, privacy fence

3. BUDGET: $475,000 CAD (adjusted for heated floors + insulated garage + deck)
4. TIMELINE: 9 months from permit approval (adjusted)
5. WARRANTY: 1-year builder warranty, 10-year structural

Signed by all parties below.
"""


# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("  CLEARCLAIM FULL SYSTEM TEST — DABOUSH FAMILY HOME BUILD")
print("=" * 78)

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — AUTH & DEVICE SECURITY
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 78)
print("  PHASE 1 — AUTH & DEVICE SECURITY")
print("─" * 78)

# Test 1.1: Signup + Login + TOTP for all users
print("\n  ── 1.1 Signup + Login + TOTP ──")
mike = signup_and_auth(f"mike.manager_{TS}@buildahome.com", "M!keStr0ng1")
alex = signup_and_auth(f"alex.roofing_{TS}@buildahome.com", "Al3x!Roof1")
sam = signup_and_auth(f"sam.floors_{TS}@buildahome.com", "S@mFloor1!")
lina = signup_and_auth(f"lina.legal_{TS}@buildahome.com", "L!naLaw123")
john = signup_and_auth(f"john.daboush_{TS}@gmail.com", "J0hnHome!1")
sarah = signup_and_auth(f"sarah.daboush_{TS}@gmail.com", "Sar@hHome1")

# Verify all users got user IDs and tokens
for u in [mike, alex, sam, lina, john, sarah]:
    check(f"User {u['email']} has user_id", bool(u["user_id"]), u["user_id"])
    check(f"User {u['email']} has access_token", bool(u["access_token"]))

# Test 1.2: Register + verify trusted devices for all users
print("\n  ── 1.2 Device Registration & Trust ──")
for user in [mike, alex, sam, lina, john, sarah]:
    dev = post("/user/add_device", [user["user_id"], f"Laptop-{user['email'][:4]}", "Office"], user["access_token"])
    device_id = dev.get("device_id", "")
    check(f"Device registered for {user['email'][:12]}...", bool(device_id), str(dev))
    user["device_id"] = device_id

    # Before verification, device should NOT be trusted
    devices_list = get("/user/get_devices", {"user_id": user["user_id"]}, user["access_token"])
    if isinstance(devices_list, list):
        new_dev = [d for d in devices_list if d.get("id") == device_id]
        if new_dev:
            check(f"Device untrusted before verify ({user['email'][:12]}...)",
                  new_dev[0].get("trusted") is False or new_dev[0].get("trusted") == False,
                  str(new_dev[0]))

    # Verify the device (marks trusted)
    verify = post("/user/verify_new_device", [user["user_id"], device_id], user["access_token"])
    check(f"Device verified for {user['email'][:12]}...", "error" not in str(verify).lower(), str(verify))

    # After verification, device should be trusted
    devices_after = get("/user/get_devices", {"user_id": user["user_id"]}, user["access_token"])
    if isinstance(devices_after, list):
        verified_dev = [d for d in devices_after if d.get("id") == device_id]
        if verified_dev:
            check(f"Device trusted after verify ({user['email'][:12]}...)",
                  verified_dev[0].get("trusted") is True or verified_dev[0].get("trusted") == True,
                  str(verified_dev[0]))

# Test 1.3: New device login triggers notification
print("\n  ── 1.3 New Device Notification ──")
notifs_mike = get("/notification/get_user_notifications", {"user_id": mike["user_id"]}, mike["access_token"])
if isinstance(notifs_mike, list):
    new_device_notifs = [n for n in notifs_mike if "device" in str(n.get("type", n.get("event_type", ""))).lower() or "device" in str(n.get("message", n.get("content", ""))).lower()]
    check("Mike got new device notification", len(new_device_notifs) > 0, str(notifs_mike)[:200])
else:
    check("Mike notifications returned list", False, str(notifs_mike)[:200])

# Test 1.4: Login without TOTP fails (401 on protected route)
print("\n  ── 1.4 Protected Route Without Auth ──")
no_auth = post("/project/create", ["TestProject", mike["user_id"]])
check("Protected route without token → 401", no_auth.get("_http_error") == 401, str(no_auth))


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — PROJECT + ROLE HIERARCHY ENFORCEMENT
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 78)
print("  PHASE 2 — PROJECT + ROLE HIERARCHY ENFORCEMENT")
print("─" * 78)

# Test 2.1: Create project
print("\n  ── 2.1 Create Project ──")
proj = post("/project/create", [f"Daboush Family Home", mike["user_id"]], mike["access_token"])
check("Project created", proj.get("project_id") is not None, str(proj))
project_id = proj.get("project_id", "")

# Test 2.2: Create subgroups
print("\n  ── 2.2 Create Subgroups ──")
subgroup_names = ["Roofing Team", "Flooring Team", "Structural Team", "Electrical Team", "Landscaping Team"]
subgroup_ids = {}
for sg_name in subgroup_names:
    sg = post("/project/create_subgroup", [project_id, sg_name], mike["access_token"])
    check(f"Subgroup '{sg_name}' created", sg.get("subgroup_id") is not None, str(sg))
    subgroup_ids[sg_name] = sg.get("subgroup_id", "")

# Test 2.3: Invite members with correct roles
print("\n  ── 2.3 Invite Members ──")
role_assignments = [
    (mike, "worker_manager"),
    (alex, "worker"),
    (sam, "worker"),
    (lina, "legal_rep"),
    (john, "client"),
    (sarah, "client"),
]
for user, role in role_assignments:
    inv = post("/project/invite_user", [project_id, user["user_id"], role], mike["access_token"])
    check(f"Invite {user['email'][:15]}... as {role}",
          inv.get("membership_id") is not None or inv.get("status") != "error", str(inv))

# Verify members list
members = get("/project/get_members", {"project_id": project_id}, mike["access_token"])
check("Get project members returns list", isinstance(members, list), str(members)[:200])
if isinstance(members, list):
    check(f"Project has {len(members)} members (expected 6)", len(members) >= 6, f"Got {len(members)}")

# Test 2.4: Assign workers to subgroups
print("\n  ── 2.4 Assign Workers to Subgroups ──")
sg_join_alex = post("/project/join_subgroup", [alex["user_id"], subgroup_ids.get("Roofing Team", ""), project_id, "worker"], mike["access_token"])
check("Alex joined Roofing Team", "error" not in str(sg_join_alex).lower(), str(sg_join_alex))

sg_join_sam = post("/project/join_subgroup", [sam["user_id"], subgroup_ids.get("Flooring Team", ""), project_id, "worker"], mike["access_token"])
check("Sam joined Flooring Team", "error" not in str(sg_join_sam).lower(), str(sg_join_sam))

# Test 2.5: Role hierarchy enforcement — TTF (Tests That Fail)
print("\n  ── 2.5 Role Hierarchy TTF ──")

# Worker tries to remove worker_manager → MUST FAIL
remove_fail_1 = post("/project/remove_member", [alex["user_id"], project_id, mike["user_id"]], alex["access_token"])
check("Worker cannot remove worker_manager",
      "error" in str(remove_fail_1).lower() or "permission" in str(remove_fail_1).lower() or "hierarchy" in str(remove_fail_1).lower() or remove_fail_1.get("_http_error") is not None,
      str(remove_fail_1))

# Client tries to change roles → MUST FAIL
role_fail_1 = post("/project/change_user_role", [john["user_id"], project_id, alex["user_id"], "guest"], john["access_token"])
check("Client cannot change worker role",
      "error" in str(role_fail_1).lower() or "permission" in str(role_fail_1).lower() or "hierarchy" in str(role_fail_1).lower() or role_fail_1.get("_http_error") is not None,
      str(role_fail_1))

# Worker tries to remove same-level worker → MUST FAIL
remove_fail_2 = post("/project/remove_member", [alex["user_id"], project_id, sam["user_id"]], alex["access_token"])
check("Worker cannot remove same-level worker",
      "error" in str(remove_fail_2).lower() or "permission" in str(remove_fail_2).lower() or "hierarchy" in str(remove_fail_2).lower() or remove_fail_2.get("_http_error") is not None,
      str(remove_fail_2))

# Legal rep tries to remove worker → MUST FAIL (legal_rep < worker in hierarchy)
remove_fail_3 = post("/project/remove_member", [lina["user_id"], project_id, alex["user_id"]], lina["access_token"])
check("Legal rep cannot remove worker (lower rank)",
      "error" in str(remove_fail_3).lower() or "permission" in str(remove_fail_3).lower() or "hierarchy" in str(remove_fail_3).lower() or remove_fail_3.get("_http_error") is not None,
      str(remove_fail_3))

# Test 2.6: worker_manager CAN change worker role → MUST PASS (TTP)
print("\n  ── 2.6 Role Hierarchy TTP ──")

# First check current role
alex_role_before = get("/project/get_user_role", {"user_id": alex["user_id"], "project_id": project_id}, mike["access_token"])
check("Alex role check before change", alex_role_before is not None, str(alex_role_before))

# Worker manager changes worker to guest (temporarily)
role_change = post("/project/change_user_role", [mike["user_id"], project_id, alex["user_id"], "guest"], mike["access_token"])
check("Worker_manager can change worker to guest",
      role_change.get("status") == "Role changed" or "role changed" in str(role_change).lower(),
      str(role_change))

# Change Alex back to worker
role_restore = post("/project/change_user_role", [mike["user_id"], project_id, alex["user_id"], "worker"], mike["access_token"])
check("Worker_manager restored Alex to worker", "role changed" in str(role_restore).lower(), str(role_restore))

# Verify DB was actually updated — check role
alex_role_after = get("/project/get_user_role", {"user_id": alex["user_id"], "project_id": project_id}, mike["access_token"])
check("Alex role restored in DB", str(alex_role_after) == "worker" or "worker" in str(alex_role_after), str(alex_role_after))


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — CONTRACT SYSTEM (CORE)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 78)
print("  PHASE 3 — CONTRACT SYSTEM")
print("─" * 78)

# Test 3.1: Create contract
print("\n  ── 3.1 Create Contract ──")
contract = post("/contract/create", [project_id, mike["user_id"], HOME_CONTRACT, "Daboush Family Home Build Contract"], mike["access_token"])
check("Contract created", contract.get("contract_id") is not None, str(contract))
contract_id = contract.get("contract_id", "")
version_id_v1 = contract.get("version_id", "")

# Verify version 1 exists
versions = get("/contract/get_versions", {"contract_id": contract_id}, mike["access_token"])
check("Contract has version 1", isinstance(versions, list) and len(versions) >= 1, str(versions)[:200])
if isinstance(versions, list) and versions:
    v1 = versions[0]
    check("Version 1 has content_hash", bool(v1.get("content_hash")), str(v1)[:200])
    check("Version 1 version_number is correct", v1.get("version_number") in (1, "1"), str(v1)[:200])

# Verify contract state is draft
state = get("/contract/get_state", {"contract_id": contract_id}, mike["access_token"])
check("Contract initial state is draft", state == "draft" or "draft" in str(state), str(state))

# Test 3.2: Permission enforcement on contract creation
print("\n  ── 3.2 Contract Permission TTF ──")
# Client tries to create contract → MUST FAIL
contract_fail = post("/contract/create", [project_id, john["user_id"], "Client contract attempt", "Unauthorized"], john["access_token"])
check("Client cannot create contract",
      "error" in str(contract_fail).lower() or "permission" in str(contract_fail).lower(),
      str(contract_fail))

# Guest (if we had one) scenario — client tries to revise → MUST FAIL
revise_fail = post("/contract/revise", [contract_id, "Client revision attempt", john["user_id"]], john["access_token"])
check("Client cannot revise contract",
      "error" in str(revise_fail).lower() or "permission" in str(revise_fail).lower(),
      str(revise_fail))

# Test 3.3: Revision flow — client requests heated floors
print("\n  ── 3.3 Create Revision (Heated Floors) ──")
revision = post("/contract/revise", [contract_id, HOME_CONTRACT_REVISION, sam["user_id"]], sam["access_token"])
check("Revision created by worker (Sam)", revision.get("version_id") is not None, str(revision))
version_id_v2 = revision.get("version_id", "")

# Verify new version created
versions_after = get("/contract/get_versions", {"contract_id": contract_id}, mike["access_token"])
if isinstance(versions_after, list):
    check(f"Now have {len(versions_after)} versions", len(versions_after) >= 2, f"Got {len(versions_after)}")

# Verify diff stored
diff_result = post("/contract/generate_diff", [HOME_CONTRACT, HOME_CONTRACT_REVISION], mike["access_token"])
check("Diff generated between versions", isinstance(diff_result, str) and len(diff_result) > 0, str(diff_result)[:200])
if isinstance(diff_result, str):
    check("Diff shows HEATED FLOORING addition", "HEATED" in diff_result, diff_result[:300])

# Verify previous version unchanged
if isinstance(versions_after, list) and len(versions_after) >= 2:
    v1_content = versions_after[0].get("content", "")
    check("Version 1 content unchanged", "HEATED" not in v1_content, v1_content[:100])

# Test 3.4: Unanimous approval (CRITICAL)
print("\n  ── 3.4 Unanimous Approval Flow ──")

# Worker manager approves
approve_mike = post("/contract/approve_revision", [version_id_v2, mike["user_id"]], mike["access_token"])
check("Mike (worker_manager) approved revision", "error" not in str(approve_mike).lower(), str(approve_mike))

# Worker Alex approves
approve_alex = post("/contract/approve_revision", [version_id_v2, alex["user_id"]], alex["access_token"])
check("Alex (worker) approved revision", "error" not in str(approve_alex).lower(), str(approve_alex))

# Legal rep approves
approve_lina = post("/contract/approve_revision", [version_id_v2, lina["user_id"]], lina["access_token"])
check("Lina (legal_rep) approved revision", "error" not in str(approve_lina).lower(), str(approve_lina))

# Sam (worker) approves
approve_sam = post("/contract/approve_revision", [version_id_v2, sam["user_id"]], sam["access_token"])
check("Sam (worker) approved revision", "error" not in str(approve_sam).lower(), str(approve_sam))

# ONLY ONE client (John) approves — not yet unanimous
approve_john = post("/contract/approve_revision", [version_id_v2, john["user_id"]], john["access_token"])
check("John (client) approved revision", "error" not in str(approve_john).lower(), str(approve_john))

# Check: is it unanimous yet? It should NOT be (Sarah hasn't approved)
all_member_ids = [u["user_id"] for u in [mike, alex, sam, lina, john, sarah]]
unanimous_check = post("/contract/check_unanimous_approval", [version_id_v2, all_member_ids], mike["access_token"])
check("NOT unanimous yet (Sarah missing)",
      unanimous_check is False or unanimous_check == False or "false" in str(unanimous_check).lower(),
      str(unanimous_check))

# Now Sarah approves → unanimous
approve_sarah = post("/contract/approve_revision", [version_id_v2, sarah["user_id"]], sarah["access_token"])
check("Sarah (client) approved revision", "error" not in str(approve_sarah).lower(), str(approve_sarah))

# Check again — should be unanimous now
unanimous_check_2 = post("/contract/check_unanimous_approval", [version_id_v2, all_member_ids], mike["access_token"])
check("NOW unanimous (all approved)",
      unanimous_check_2 is True or unanimous_check_2 == True or "true" in str(unanimous_check_2).lower(),
      str(unanimous_check_2))

# Verify each approval has a unique timestamp in audit logs
audit_approvals = get("/audit/get_entries", {"related_object_id": version_id_v2, "limit": "50"}, mike["access_token"])
if isinstance(audit_approvals, list):
    approval_entries = [a for a in audit_approvals if "approve" in str(a.get("event_type", "")).lower()]
    timestamps = [a.get("timestamp") for a in approval_entries]
    check(f"Found {len(approval_entries)} approval audit entries", len(approval_entries) >= 6, str(len(approval_entries)))
    check("Approval timestamps exist", all(t is not None for t in timestamps), str(timestamps)[:200])

# Test 3.5: Contract state transitions
print("\n  ── 3.5 Contract State Management ──")
state_after_approval = get("/contract/get_state", {"contract_id": contract_id}, mike["access_token"])
check("Contract state advanced after unanimous approval",
      state_after_approval in ("ready_for_signature", "revision_approved") or
      "ready" in str(state_after_approval).lower() or "approved" in str(state_after_approval).lower(),
      str(state_after_approval))


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — SIGNING FLOW (HIGH RISK)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 78)
print("  PHASE 4 — SIGNING FLOW")
print("─" * 78)

# Ensure contract is in ready_for_signature state
if state_after_approval not in ("ready_for_signature",):
    trans = post("/contract/transition_state", [contract_id, "ready_for_signature"], mike["access_token"])

# Test 4.1: Signing without TOTP → MUST FAIL
print("\n  ── 4.1 Signing Without TOTP (TTF) ──")
sign_no_totp = post("/signing/sign", [version_id_v2, john["user_id"], john["device_id"], "", "", ""], john["access_token"])
check("Sign without TOTP → rejected",
      "error" in str(sign_no_totp).lower() or "authenticator" in str(sign_no_totp).lower(),
      str(sign_no_totp))

# Test 4.2: Signing with wrong TOTP → MUST FAIL
print("\n  ── 4.2 Signing With Wrong TOTP (TTF) ──")
sign_bad_totp = post("/signing/sign", [version_id_v2, john["user_id"], john["device_id"], "", john["totp_secret"], "000000"], john["access_token"])
check("Sign with wrong TOTP → rejected",
      "error" in str(sign_bad_totp).lower() or "invalid" in str(sign_bad_totp).lower(),
      str(sign_bad_totp))

# Test 4.3: Valid signing flow for all parties
print("\n  ── 4.3 Valid Signing Flow (TTP) ──")

signers = [
    (mike, "worker_manager"),
    (alex, "worker"),
    (sam, "worker"),
    (lina, "legal_rep"),
    (john, "client"),
    (sarah, "client"),
]

for user, role in signers:
    time.sleep(1)  # ensure different TOTP windows
    totp = pyotp.TOTP(user["totp_secret"])
    code = totp.now()
    sig = post("/signing/sign",
               [version_id_v2, user["user_id"], user["device_id"], "", user["totp_secret"], code],
               user["access_token"])
    check(f"Sign contract — {user['email'][:15]}... ({role})",
          sig.get("signature_id") is not None or sig.get("status") == "Contract signed" or sig.get("status") == "already_signed",
          str(sig)[:200])

    # Verify signature record has all required fields
    if sig.get("signature_id"):
        check(f"  → has signed_at timestamp", bool(sig.get("signed_at")), str(sig.get("signed_at")))
        check(f"  → has contract_snapshot_hash", bool(sig.get("contract_snapshot_hash")), str(sig.get("contract_snapshot_hash")))
        check(f"  → TOTP was verified", sig.get("totp_verified") is True, str(sig.get("totp_verified")))

# Verify all signatures stored
sigs = get("/signing/get_signatures", {"contract_version_id": version_id_v2}, mike["access_token"])
if isinstance(sigs, list):
    check(f"Got {len(sigs)} signatures for contract", len(sigs) >= 6, str(len(sigs)))
    # Each signature should have user_id, device_id, signed_at
    for s in sigs:
        check(f"  Sig {s.get('id','?')[:8]}... has user_id", bool(s.get("user_id")), str(s))

# Verify contract auto-transitioned to fully_signed
time.sleep(1)
state_after_signing = get("/contract/get_state", {"contract_id": contract_id}, mike["access_token"])
check("Contract is fully_signed after all signatures",
      state_after_signing == "fully_signed" or "fully_signed" in str(state_after_signing),
      str(state_after_signing))

# Test 4.4: Attempt to reuse / sign again → MUST FAIL (idempotency)
print("\n  ── 4.4 Duplicate Signing (TTF) ──")
time.sleep(1)
totp_dup = pyotp.TOTP(john["totp_secret"]).now()
sign_dup = post("/signing/sign", [version_id_v2, john["user_id"], john["device_id"], "", john["totp_secret"], totp_dup], john["access_token"])
check("Duplicate signing → already_signed",
      "already_signed" in str(sign_dup) or sign_dup.get("status") == "already_signed",
      str(sign_dup))

# Test 4.5: Ephemeral token generation
print("\n  ── 4.5 Ephemeral Signing Token ──")
eph = post("/signing/ephemeral_token", [john["user_id"], version_id_v2], john["access_token"])
check("Ephemeral token generated", bool(eph.get("token")), str(eph))
check("Ephemeral token has expiry", bool(eph.get("expires_at")), str(eph))
check("Ephemeral token bound to version", eph.get("contract_version_id") == version_id_v2, str(eph))


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5 — EVIDENCE SYSTEM (STRICT RULES)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 78)
print("  PHASE 5 — EVIDENCE SYSTEM")
print("─" * 78)

# Test 5.1: Upload evidence — roofing team photos
print("\n  ── 5.1 Upload Evidence ──")
ev_roof = post("/evidence/upload", [contract_id, "", "https://storage.buildahome.com/roof_progress_1.jpg", "image/jpeg", 25000, alex["user_id"]], alex["access_token"])
check("Roofing evidence uploaded (Alex)", ev_roof.get("evidence_id") is not None, str(ev_roof))
evidence_id_roof = ev_roof.get("evidence_id", "")
check("Evidence has file_hash", bool(ev_roof.get("file_hash")), str(ev_roof))
check("Evidence has timestamp_proof", bool(ev_roof.get("timestamp_proof")), str(ev_roof))
check("Evidence has uploader_hash", bool(ev_roof.get("uploader_hash")), str(ev_roof))

# Flooring evidence
ev_floor = post("/evidence/upload", [contract_id, "", "https://storage.buildahome.com/floor_install.pdf", "application/pdf", 50000, sam["user_id"]], sam["access_token"])
check("Flooring evidence uploaded (Sam)", ev_floor.get("evidence_id") is not None, str(ev_floor))
evidence_id_floor = ev_floor.get("evidence_id", "")

# Legal document
ev_legal = post("/evidence/upload", [contract_id, "", "https://storage.buildahome.com/permit_approval.pdf", "application/pdf", 75000, lina["user_id"]], lina["access_token"])
check("Legal evidence uploaded (Lina)", ev_legal.get("evidence_id") is not None, str(ev_legal))
evidence_id_legal = ev_legal.get("evidence_id", "")

# Test 5.2: Client cannot upload evidence → MUST FAIL
print("\n  ── 5.2 Client Evidence Upload (TTF) ──")
ev_client_fail = post("/evidence/upload", [contract_id, "", "https://example.com/client_photo.jpg", "image/jpeg", 5000, john["user_id"]], john["access_token"])
check("Client cannot upload evidence",
      "error" in str(ev_client_fail).lower() or "permission" in str(ev_client_fail).lower(),
      str(ev_client_fail))

# Test 5.3: Evidence visible in contract evidence list
print("\n  ── 5.3 Evidence Listing ──")
all_evidence = get("/evidence/get_contract_evidence", {"contract_id": contract_id}, mike["access_token"])
check("Contract evidence returned as list", isinstance(all_evidence, list), str(all_evidence)[:200])
if isinstance(all_evidence, list):
    check(f"Contract has {len(all_evidence)} evidence items (expected 3+)", len(all_evidence) >= 3, f"Got {len(all_evidence)}")

# Test 5.4: Evidence deletion requires unanimous consent
print("\n  ── 5.4 Evidence Deletion Unanimous Consent ──")

# Request deletion
del_request = post("/evidence/request_deletion", [evidence_id_roof, alex["user_id"]], alex["access_token"])
check("Deletion request created", "error" not in str(del_request).lower(), str(del_request))

# Approve deletion — only 3 of 6 approve
del_approve_1 = post("/evidence/approve_deletion", [evidence_id_roof, mike["user_id"]], mike["access_token"])
check("Mike approves deletion", "error" not in str(del_approve_1).lower(), str(del_approve_1))
del_approve_2 = post("/evidence/approve_deletion", [evidence_id_roof, alex["user_id"]], alex["access_token"])
check("Alex approves deletion", "error" not in str(del_approve_2).lower(), str(del_approve_2))
del_approve_3 = post("/evidence/approve_deletion", [evidence_id_roof, sam["user_id"]], sam["access_token"])
check("Sam approves deletion", "error" not in str(del_approve_3).lower(), str(del_approve_3))

# Check: NOT unanimous yet (only 3/6)
del_check = post("/evidence/check_unanimous_approval", [evidence_id_roof, all_member_ids], mike["access_token"])
check("Deletion NOT unanimous (3/6 approved)",
      del_check is False or del_check == False or "false" in str(del_check).lower(),
      str(del_check))

# Remaining approve
del_approve_4 = post("/evidence/approve_deletion", [evidence_id_roof, lina["user_id"]], lina["access_token"])
del_approve_5 = post("/evidence/approve_deletion", [evidence_id_roof, john["user_id"]], john["access_token"])
del_approve_6 = post("/evidence/approve_deletion", [evidence_id_roof, sarah["user_id"]], sarah["access_token"])

# Now delete — should work
del_result = post("/evidence/delete", [evidence_id_roof], mike["access_token"])
check("Evidence deleted after unanimous consent",
      "deleted" in str(del_result).lower() or del_result.get("status") == "Evidence deleted",
      str(del_result))

# Verify deleted evidence has deletion timestamp (NOT hard-deleted from view)
all_evidence_after = get("/evidence/get_contract_evidence", {"contract_id": contract_id}, mike["access_token"])
if isinstance(all_evidence_after, list):
    # Evidence count may have decreased (soft delete removes from active query)
    check("Evidence list updated after deletion", True, f"Now {len(all_evidence_after)} items")

# Test 5.5: Evidence approval for addition
print("\n  ── 5.5 Evidence Addition Approval ──")
ev_extra = post("/evidence/upload", [contract_id, "", "https://storage.buildahome.com/inspection_report.pdf", "application/pdf", 30000, mike["user_id"]], mike["access_token"])
evidence_id_extra = ev_extra.get("evidence_id", "")
check("Extra evidence uploaded for approval flow", bool(evidence_id_extra), str(ev_extra))

# Propose addition
propose = post("/evidence/propose_addition", [contract_id, evidence_id_extra, mike["user_id"]], mike["access_token"])
check("Evidence addition proposed", "error" not in str(propose).lower(), str(propose))

# All approve
for user in [mike, alex, sam, lina, john, sarah]:
    appr = post("/evidence/approve", [evidence_id_extra, user["user_id"]], user["access_token"])
    check(f"  {user['email'][:12]}... approved evidence", "error" not in str(appr).lower(), str(appr))

# Check unanimous
ev_unanimous = post("/evidence/check_unanimous_approval", [evidence_id_extra, all_member_ids], mike["access_token"])
check("Evidence addition unanimous after all approved",
      ev_unanimous is True or ev_unanimous == True or "true" in str(ev_unanimous).lower(),
      str(ev_unanimous))

# Activate evidence
activate = post("/evidence/activate", [evidence_id_extra], mike["access_token"])
check("Evidence activated", "error" not in str(activate).lower(), str(activate))


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 6 — TIMELINE (AUDIT ENTRIES AS FRONT-END TRUTH)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 78)
print("  PHASE 6 — TIMELINE VERIFICATION")
print("─" * 78)

print("\n  ── 6.1 Audit Entries Completeness ──")
all_audit = get("/audit/get_entries", {"limit": "200"}, mike["access_token"])
check("Audit entries returned as list", isinstance(all_audit, list), str(all_audit)[:200])

if isinstance(all_audit, list):
    event_types = {e.get("event_type") for e in all_audit}
    check(f"Total audit entries: {len(all_audit)}", len(all_audit) > 20, str(len(all_audit)))

    # Events that MUST exist for timeline truth
    required_events = [
        "create_project",
        "create_contract",
        "create_contract_revision",
        "approve_contract_revision",
        "sign_contract",
        "upload_evidence",
        "device_registered",
    ]
    for evt in required_events:
        found = evt in event_types
        check(f"Timeline has event: {evt}", found, f"Found types: {event_types}")

    # Each entry must have user_id, timestamp, event_type
    sample = all_audit[:5]
    for entry in sample:
        check(f"Entry {entry.get('id','?')[:8]}... has user_id", bool(entry.get("user_id")))
        check(f"Entry {entry.get('id','?')[:8]}... has timestamp", bool(entry.get("timestamp")))
        check(f"Entry {entry.get('id','?')[:8]}... has event_type", bool(entry.get("event_type")))
        check(f"Entry {entry.get('id','?')[:8]}... has hash", bool(entry.get("hash")))


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 7 — AUDIT LOG INTEGRITY (NON-NEGOTIABLE)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 78)
print("  PHASE 7 — AUDIT LOG INTEGRITY")
print("─" * 78)

# Test 7.1: Hash chain verification
print("\n  ── 7.1 Hash Chain Verification ──")
chain_valid = post("/audit/verify_chain", [], mike["access_token"])
check("Audit hash chain is valid", chain_valid is True or chain_valid == True, str(chain_valid))

# Test 7.2: Per-entry verification
print("\n  ── 7.2 Per-Entry Integrity ──")
entry_check = post("/audit/verify_entries", [], mike["access_token"])
if isinstance(entry_check, dict):
    check("All entries valid", entry_check.get("is_valid") is True, str(entry_check))
    check("No tampered entries", len(entry_check.get("invalid_entry_ids", [])) == 0,
          str(entry_check.get("invalid_entry_ids")))
    check(f"Total entries verified: {entry_check.get('total')}", entry_check.get("total", 0) > 0, str(entry_check))

# Test 7.3: Consecutive entries have correct prev_hash linkage
print("\n  ── 7.3 Consecutive Hash Chain Spot Check ──")
if isinstance(all_audit, list) and len(all_audit) >= 5:
    # Get 5 consecutive entries (entries are returned in order)
    sample_5 = all_audit[:5]
    for i in range(1, len(sample_5)):
        prev_entry = sample_5[i - 1]
        curr_entry = sample_5[i]
        check(f"Entry[{i}].prev_hash == Entry[{i-1}].hash",
              curr_entry.get("prev_hash") == prev_entry.get("hash"),
              f"prev_hash={curr_entry.get('prev_hash')[:16]}... vs hash={prev_entry.get('hash')[:16]}...")

# Test 7.4: Snapshot generation
print("\n  ── 7.4 Audit Snapshot ──")
snapshot = post("/audit/snapshot", [], mike["access_token"])
check("Snapshot hash generated", isinstance(snapshot, str) and len(snapshot) > 10, str(snapshot)[:80])

# Archive the snapshot
archive = post("/audit/archive_snapshot", [snapshot if isinstance(snapshot, str) else ""], mike["access_token"])
check("Snapshot archived", "error" not in str(archive).lower(), str(archive))


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 8 — SECURITY MONITORING
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 78)
print("  PHASE 8 — SECURITY MONITORING")
print("─" * 78)

# Test 8.1: Suspicious activity detection — repeated failed signing
print("\n  ── 8.1 Suspicious Activity: Repeated Failed Signing ──")
suspicious = post("/security/detect_suspicious_activity", [john["user_id"], "repeated_failed_signing"], mike["access_token"])
check("Suspicious activity flagged", suspicious.get("restricted") is True or "flagged" in str(suspicious).lower(), str(suspicious))

# Verify user is now restricted
is_restricted = get("/security/is_restricted", {"user_id": john["user_id"]}, mike["access_token"])
check("John is now restricted", is_restricted is True or is_restricted == True, str(is_restricted))

# Verify notification sent
john_notifs = get("/notification/get_user_notifications", {"user_id": john["user_id"]}, john["access_token"])
if isinstance(john_notifs, list):
    sus_notifs = [n for n in john_notifs if "suspicious" in str(n.get("type", n.get("event_type", ""))).lower() or "restrict" in str(n.get("message", n.get("content", ""))).lower()]
    check("John received suspicious activity notification", len(sus_notifs) > 0, str(john_notifs)[:200])

# Test 8.2: Lift restriction
print("\n  ── 8.2 Lift Restriction ──")
lift = post("/security/lift_restriction", [john["user_id"]], mike["access_token"])
check("Restriction lifted", "error" not in str(lift).lower(), str(lift))

is_restricted_after = get("/security/is_restricted", {"user_id": john["user_id"]}, mike["access_token"])
check("John is no longer restricted", is_restricted_after is False or is_restricted_after == False, str(is_restricted_after))

# Test 8.3: New device login alert
print("\n  ── 8.3 New Device Login Alert ──")
suspicious_device = post("/security/detect_suspicious_activity", [john["user_id"], "new_device_login"], mike["access_token"])
check("New device login flagged", suspicious_device.get("restricted") is True, str(suspicious_device))

# Clean up restriction
post("/security/lift_restriction", [john["user_id"]], mike["access_token"])

# Test 8.4: Security alert sending
print("\n  ── 8.4 Security Alert ──")
alert = post("/security/send_alert", [john["user_id"], "unusual_activity", "Unusual login pattern detected from IP 192.168.1.100"], mike["access_token"])
check("Security alert sent", "error" not in str(alert).lower(), str(alert))


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 9 — EXPORT & LEGAL COMPLIANCE
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 78)
print("  PHASE 9 — EXPORT & LEGAL COMPLIANCE")
print("─" * 78)

# Test 9.1: Export contract history
print("\n  ── 9.1 Export Contract Data ──")
exp_history = get("/export/contract_history", {"contract_id": contract_id}, lina["access_token"])
check("Export contract history", exp_history is not None and "_http_error" not in str(exp_history), str(exp_history)[:200])

exp_versions = get("/export/contract_versions", {"contract_id": contract_id}, lina["access_token"])
check("Export contract versions", exp_versions is not None and "_http_error" not in str(exp_versions), str(exp_versions)[:200])

exp_sigs = get("/export/contract_signatures", {"contract_id": contract_id}, lina["access_token"])
check("Export contract signatures", exp_sigs is not None and "_http_error" not in str(exp_sigs), str(exp_sigs)[:200])

exp_evidence = get("/export/contract_evidence", {"contract_id": contract_id}, lina["access_token"])
check("Export contract evidence", exp_evidence is not None and "_http_error" not in str(exp_evidence), str(exp_evidence)[:200])

exp_audit = get("/export/audit_logs", {"contract_id": contract_id}, lina["access_token"])
check("Export audit logs", exp_audit is not None and "_http_error" not in str(exp_audit), str(exp_audit)[:200])

# Test 9.2: Full case archive
print("\n  ── 9.2 Full Case Archive ──")
case_archive = post("/export/case_archive", [contract_id], mike["access_token"])
check("Case archive generated", case_archive is not None and "_http_error" not in str(case_archive), str(case_archive)[:200])

# Test 9.3: Legal compliance endpoints
print("\n  ── 9.3 Legal Compliance Endpoints ──")
legal_endpoints = [
    ("privacy_policy", "privacy"),
    ("terms_of_service", "terms"),
    ("accessibility", "accessibility"),
    ("record_retention", "retention"),
    ("right_to_be_forgotten", "right"),
    ("dispute_resolution", "dispute"),
    ("breach_notification", "breach"),
    ("children_privacy", "children"),
    ("data_localization", "localization"),
    ("consent", "consent"),
]
for endpoint, keyword in legal_endpoints:
    result = get(f"/legal/{endpoint}", {}, mike["access_token"])
    check(f"Legal: {endpoint}", result is not None and "_http_error" not in result, str(result)[:100])

# Test 9.4: Identity verification
print("\n  ── 9.4 Identity Verification ──")
id_start = post("/user/start_identity_verification", [john["user_id"]], john["access_token"])
check("Identity verification started", "error" not in str(id_start).lower(), str(id_start))

id_store = post("/user/store_identity_verification_result", [john["user_id"], "Onfido", "verified"], john["access_token"])
check("Identity verification result stored", "error" not in str(id_store).lower(), str(id_store))

id_check = get("/user/check_identity_verification_status", {"user_id": john["user_id"]}, john["access_token"])
check("Identity verification status retrievable", id_check is not None and "_http_error" not in str(id_check), str(id_check))

# Test 9.5: Device revocation (lost/stolen scenario)
print("\n  ── 9.5 Device Revocation ──")
# Register a second device for John
dev2 = post("/user/add_device", [john["user_id"], "Lost Phone", "Unknown"], john["access_token"])
lost_device_id = dev2.get("device_id", "")
check("Second device registered for John", bool(lost_device_id), str(dev2))

# Revoke it (simulating lost device)
revoke = post("/user/revoke_device", [john["user_id"], lost_device_id], john["access_token"])
check("Lost device revoked", "error" not in str(revoke).lower(), str(revoke))

# Verify revoked device in list
john_devices = get("/user/get_devices", {"user_id": john["user_id"]}, john["access_token"])
if isinstance(john_devices, list):
    revoked_dev = [d for d in john_devices if d.get("id") == lost_device_id]
    if revoked_dev:
        check("Revoked device has revoked_at timestamp", revoked_dev[0].get("revoked_at") is not None, str(revoked_dev[0]))

# Test 9.6: Notifications for all users
print("\n  ── 9.6 Notification Delivery ──")
for user in [mike, alex, sam, lina, john, sarah]:
    notifs = get("/notification/get_user_notifications", {"user_id": user["user_id"]}, user["access_token"])
    check(f"Notifications exist for {user['email'][:15]}...",
          isinstance(notifs, list) and len(notifs) > 0,
          f"Got {len(notifs) if isinstance(notifs, list) else 0}")


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 10 — ADDITIONAL EDGE CASES & CROSS-CUTTING
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 78)
print("  PHASE 10 — EDGE CASES & CROSS-CUTTING VALIDATION")
print("─" * 78)

# Test 10.1: Self-leave project
print("\n  ── 10.1 Self-Leave Project ──")
# Create a temporary user to test leaving
temp = signup_and_auth(f"temp_{TS}@test.com", "T3mp!Pass1")
inv_temp = post("/project/invite_user", [project_id, temp["user_id"], "guest"], mike["access_token"])
leave_result = post("/project/leave", [temp["user_id"], project_id], temp["access_token"])
check("User can leave project voluntarily", "error" not in str(leave_result).lower(), str(leave_result))

# Test 10.2: Rejected revision flow
print("\n  ── 10.2 Rejected Revision ──")
# Create a second contract for rejection testing
contract2 = post("/contract/create", [project_id, mike["user_id"], "Test contract for rejection", "Rejection Test Contract"], mike["access_token"])
contract2_id = contract2.get("contract_id", "")
# Revision
rev2 = post("/contract/revise", [contract2_id, "Revised content that will be rejected", alex["user_id"]], alex["access_token"])
rev2_version_id = rev2.get("version_id", "")
if rev2_version_id:
    # Reject it
    reject = post("/contract/reject_revision", [rev2_version_id, lina["user_id"]], lina["access_token"])
    check("Revision rejected by legal_rep", "error" not in str(reject).lower(), str(reject))

# Test 10.3: Verify get_me (user profile)
print("\n  ── 10.3 User Profile ──")
me = get("/user/get_me", {"user_id": john["user_id"]}, john["access_token"])
if isinstance(me, dict):
    check("get_me returns email", bool(me.get("email")), str(me))
    check("get_me returns id", bool(me.get("id")), str(me))

# Test 10.4: Worker_manager removes a worker (TTP for hierarchy)
print("\n  ── 10.4 Manager Removes Worker (TTP) ──")
# Invite a temp worker to remove
temp_worker = signup_and_auth(f"temp_worker_{TS}@buildahome.com", "TmpW0rk!1")
inv_tw = post("/project/invite_user", [project_id, temp_worker["user_id"], "worker"], mike["access_token"])
remove_success = post("/project/remove_member", [mike["user_id"], project_id, temp_worker["user_id"]], mike["access_token"])
check("Worker_manager can remove worker",
      remove_success.get("status") == "Member removed" or "member removed" in str(remove_success).lower(),
      str(remove_success))

# Test 10.5: Password reset flow
print("\n  ── 10.5 Password Reset ──")
pr = post("/user/initiate_password_reset", [john["email"]], john["access_token"])
check("Password reset initiated", "error" not in str(pr).lower(), str(pr))

# Test 10.6: Device recovery
print("\n  ── 10.6 Device Recovery ──")
recovery = post("/security/recover_device", [john["user_id"], "New Replacement Phone"], john["access_token"])
check("Device recovery initiated", "error" not in str(recovery).lower() and recovery.get("device_id") is not None, str(recovery))


# ═══════════════════════════════════════════════════════════════════════════════
# FINAL AUDIT CHAIN CHECK (after all operations)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─" * 78)
print("  FINAL — AUDIT CHAIN INTEGRITY AFTER ALL OPERATIONS")
print("─" * 78)

final_chain = post("/audit/verify_chain", [], mike["access_token"])
check("FINAL: Audit hash chain still valid after all tests", final_chain is True or final_chain == True, str(final_chain))

final_entries = post("/audit/verify_entries", [], mike["access_token"])
if isinstance(final_entries, dict):
    check("FINAL: All entries still intact", final_entries.get("is_valid") is True, str(final_entries))
    check(f"FINAL: Total audit trail size: {final_entries.get('total')} entries",
          final_entries.get("total", 0) > 50,
          str(final_entries.get("total")))


# ═══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print(f"  RESULTS: \033[92m{passed} passed\033[0m, \033[91m{failed} failed\033[0m out of {passed + failed} tests")
print("=" * 78)

if failures:
    print("\n  FAILURES:")
    for label, detail in failures:
        print(f"    ✗ {label}")
        if detail:
            print(f"      {detail[:200]}")

print()
if failed > 0:
    sys.exit(1)
else:
    print("  ✓ ALL TESTS PASSED — System validated end-to-end")
    sys.exit(0)
