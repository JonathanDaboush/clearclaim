"""Centralised input validation boundary.

All validation that needs to happen at more than one layer lives here.
Services import and call these validators before persisting anything, so bad
data is caught consistently regardless of which route triggered the request.

Layer rules:
  - API layer   → call validate_*() to return user-facing error strings early
  - Service layer → call assert_*() to raise ValueError on invariant violations
  - DB layer    → the DB schema enforces NOT NULL / UNIQUE / FOREIGN KEY as the
                  last line of defence

Design: functions raise ValidationError (a ValueError subclass) so callers
can catch it with a single except clause.
"""

from __future__ import annotations

import re
import uuid
from typing import Any


class ValidationError(ValueError):
    """Raised when an input fails a validation rule."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


# ── Primitive validators ──────────────────────────────────────────────────────

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_UUID_RE  = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def assert_non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(field, "must be a non-empty string")
    return value.strip()


def assert_valid_uuid(value: Any, field: str) -> str:
    s = assert_non_empty_string(value, field)
    if not _UUID_RE.match(s):
        raise ValidationError(field, f"must be a valid UUID (got {s!r})")
    return s


def assert_valid_email(value: Any, field: str = "email") -> str:
    s = assert_non_empty_string(value, field)
    if not _EMAIL_RE.match(s):
        raise ValidationError(field, f"must be a valid email address (got {s!r})")
    return s.lower()


def assert_min_length(value: str, field: str, min_len: int) -> str:
    if len(value) < min_len:
        raise ValidationError(field, f"must be at least {min_len} characters long")
    return value


def assert_positive_number(value: Any, field: str) -> float:
    try:
        n = float(value)
    except (TypeError, ValueError):
        raise ValidationError(field, "must be a number")
    if n <= 0:
        raise ValidationError(field, "must be a positive number")
    return n


# ── Domain-specific validators ────────────────────────────────────────────────

ALLOWED_EVIDENCE_TYPES = {"pdf", "png", "jpg", "jpeg", "docx"}
MAX_EVIDENCE_SIZE = 50 * 1024 * 1024   # 50 MB
MIN_PASSWORD_LEN  = 8
MAX_CONTRACT_CONTENT_LEN = 500_000     # 500 KB plain text


def validate_user_signup(email: str, password: str) -> None:
    assert_valid_email(email, "email")
    assert_non_empty_string(password, "password")
    assert_min_length(password, "password", MIN_PASSWORD_LEN)


def validate_contract_content(content: Any) -> str:
    s = assert_non_empty_string(content, "content")
    if len(s) > MAX_CONTRACT_CONTENT_LEN:
        raise ValidationError(
            "content",
            f"contract content exceeds maximum length ({MAX_CONTRACT_CONTENT_LEN} chars)",
        )
    return s


def validate_evidence_file(file_type: Any, file_size: Any) -> None:
    ft = assert_non_empty_string(file_type, "file_type").lower()
    if ft not in ALLOWED_EVIDENCE_TYPES:
        raise ValidationError(
            "file_type",
            f"file type {ft!r} is not allowed. Allowed: {sorted(ALLOWED_EVIDENCE_TYPES)}",
        )
    try:
        size = int(file_size)
    except (TypeError, ValueError):
        raise ValidationError("file_size", "must be an integer")
    if size <= 0:
        raise ValidationError("file_size", "must be greater than 0")
    if size > MAX_EVIDENCE_SIZE:
        raise ValidationError(
            "file_size",
            f"file size {size} exceeds maximum allowed size ({MAX_EVIDENCE_SIZE})",
        )


def validate_payment(amount: Any, method: Any) -> None:
    assert_positive_number(amount, "amount")
    assert_non_empty_string(method, "method")


def validate_idempotency_key(key: Any) -> None:
    """Idempotency keys must be UUIDs; callers may omit them (None/'' = no protection)."""
    if key is None or key == '':
        return
    assert_valid_uuid(key, "idempotency_key")


def validate_contract_state_transition(current_state: str, new_state: str) -> None:
    from utils.contract_state_utils import VALID_TRANSITIONS
    allowed = VALID_TRANSITIONS.get(current_state, set())
    if new_state not in allowed:
        raise ValidationError(
            "new_state",
            f"transition from {current_state!r} to {new_state!r} is not permitted. "
            f"Allowed: {sorted(allowed)}",
        )
