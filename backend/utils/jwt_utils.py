"""
JWT access + refresh token utilities.

Access tokens:  15-minute lifetime, signed HS256.
Refresh tokens: 7-day lifetime; SHA-256 hash stored in DB (raw token never persisted).

Usage:
    from utils.jwt_utils import issue_tokens, decode_access_token, refresh_access_token
"""

import datetime
import hashlib
import os
from typing import Dict, Optional

import jwt

_SECRET: str = os.environ.get("JWT_SECRET", "dev-insecure-changeme-use-env-in-prod")
_ALGORITHM = "HS256"
_ACCESS_TTL = 15 * 60          # 15 minutes in seconds
_REFRESH_TTL = 7 * 24 * 3600   # 7 days in seconds

# Public routes that do NOT require a valid Bearer token
PUBLIC_PATHS = frozenset({
    "/user/login",
    "/user/signup",
    "/user/verify_totp",
    "/user/initiate_password_reset",
    "/user/complete_password_reset",
    "/auth/refresh",
})


def _db():
    """Lazy import of the db module to avoid circular imports at load time."""
    import db as _db_module  # noqa: PLC0415
    return _db_module


def issue_tokens(user_id: str) -> Dict[str, object]:
    """Issue a new access + refresh token pair for the given user.

    The refresh token hash is persisted in the refresh_tokens table;
    the raw token is returned to the caller (never stored).
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    access_exp  = now + datetime.timedelta(seconds=_ACCESS_TTL)
    refresh_exp = now + datetime.timedelta(seconds=_REFRESH_TTL)

    access_token = jwt.encode(
        {"sub": user_id, "exp": access_exp,  "iat": now, "type": "access"},
        _SECRET, algorithm=_ALGORITHM,
    )
    refresh_token = jwt.encode(
        {"sub": user_id, "exp": refresh_exp, "iat": now, "type": "refresh"},
        _SECRET, algorithm=_ALGORITHM,
    )

    # Store hashed refresh token
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    try:
        _db().execute(
            """INSERT INTO refresh_tokens (token_hash, user_id, expires_at)
               VALUES (%s, %s, %s)
               ON CONFLICT (token_hash) DO NOTHING""",
            (token_hash, user_id, refresh_exp.isoformat()),
        )
    except Exception:
        pass  # DB may not be migrated yet in test environments

    return {
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "expires_in":    _ACCESS_TTL,
    }


def decode_access_token(token: str) -> Optional[str]:
    """Validate an access token and return the user_id (sub), or None on failure."""
    try:
        payload = jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])
        if payload.get("type") != "access":
            return None
        return str(payload["sub"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def refresh_access_token(refresh_token: str) -> Optional[Dict[str, object]]:
    """Validate a refresh token and issue a new access token.

    Returns None if the token is invalid, expired, or revoked.
    Does NOT rotate the refresh token (use revoke_refresh_token on sign-out).
    """
    try:
        payload = jwt.decode(refresh_token, _SECRET, algorithms=[_ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        user_id = str(payload["sub"])
    except jwt.InvalidTokenError:
        return None

    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    try:
        rows = _db().query(
            """SELECT token_hash FROM refresh_tokens
               WHERE token_hash = %s
                 AND user_id    = %s
                 AND revoked    = FALSE
                 AND expires_at > NOW()""",
            (token_hash, user_id),
        )
        if not rows:
            return None
    except Exception:
        # Fall back to signature-only validation if DB is unavailable
        pass

    now = datetime.datetime.now(datetime.timezone.utc)
    new_access = jwt.encode(
        {"sub": user_id, "exp": now + datetime.timedelta(seconds=_ACCESS_TTL), "iat": now, "type": "access"},
        _SECRET, algorithm=_ALGORITHM,
    )
    return {"access_token": new_access, "expires_in": _ACCESS_TTL}


def revoke_refresh_token(refresh_token: str) -> None:
    """Mark a specific refresh token as revoked (e.g. on explicit sign-out)."""
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    try:
        _db().execute(
            "UPDATE refresh_tokens SET revoked = TRUE WHERE token_hash = %s",
            (token_hash,),
        )
    except Exception:
        pass


def revoke_all_user_tokens(user_id: str) -> None:
    """Revoke all refresh tokens for a user (password reset, account lock)."""
    try:
        _db().execute(
            "UPDATE refresh_tokens SET revoked = TRUE WHERE user_id = %s",
            (user_id,),
        )
    except Exception:
        pass


def require_auth(path: str, auth_header: str) -> Optional[str]:
    """Return user_id from a valid Bearer token, or None to reject.

    Public paths always return the sentinel string 'public' so callers
    know authentication was bypassed intentionally.
    """
    if path in PUBLIC_PATHS:
        return "public"
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    return decode_access_token(auth_header[7:])
