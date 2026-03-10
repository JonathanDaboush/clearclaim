import uuid
import hashlib
import difflib
import secrets
from datetime import datetime, timezone


def hash_password(password: str) -> str:
    """Return a secure SHA-256 hash of the password. Use bcrypt/argon2 in production."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Return True if hash_password(password) matches the stored hash."""
    return hash_password(password) == password_hash


def generate_uuid() -> str:
    """Return a new UUID4 string."""
    return str(uuid.uuid4())


def current_utc_timestamp() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


from typing import List, Dict


def compute_diff(old_text: str, new_text: str) -> Dict[str, List[str]]:
    """Return a line-by-line diff between old_text and new_text."""
    added: List[str] = []
    removed: List[str] = []
    for line in difflib.unified_diff(old_text.splitlines(), new_text.splitlines(), lineterm=""):
        if line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
        elif line.startswith("-") and not line.startswith("---"):
            removed.append(line[1:])
    return {"added": added, "removed": removed}


def generate_ephemeral_token(user_id: str, contract_version_id: str) -> str:
    """Return a secure one-time token bound to a user and contract version."""
    raw = f"{user_id}:{contract_version_id}:{secrets.token_hex(16)}"
    return hashlib.sha256(raw.encode()).hexdigest()
