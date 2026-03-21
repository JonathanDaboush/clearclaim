import hashlib
import hmac
import secrets
import pyotp as _pyotp  # type: ignore[import-untyped]
from typing import Any, cast

pyotp = cast(Any, _pyotp)


def hash_password(password: str) -> str:
    """Return a bcrypt hash of the password (cost factor 12)."""
    try:
        import bcrypt as _bcrypt
        return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt(rounds=12)).decode()
    except ImportError:
        # bcrypt not installed — fall back to SHA-256 (dev-only, insecure)
        return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Return True if password matches the stored hash.

    Handles both bcrypt hashes (preferred) and legacy SHA-256 hashes.
    """
    if password_hash.startswith("$2"):
        # bcrypt hash
        try:
            import bcrypt as _bcrypt
            return _bcrypt.checkpw(password.encode(), password_hash.encode())
        except Exception:
            return False
    # Legacy SHA-256 hash — constant-time comparison
    return hmac.compare_digest(hashlib.sha256(password.encode()).hexdigest(), password_hash)


def generate_totp_secret() -> str:
    """Generate a new Base32 TOTP secret key."""
    return pyotp.random_base32()


def verify_totp(secret: str, code: str) -> bool:
    """Return True if the TOTP code is valid for the given secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def generate_secure_token() -> str:
    """Return a cryptographically secure random hex token."""
    return secrets.token_hex(32)


def hash_data(data: str) -> str:
    """Return a SHA-256 hash of the given data string."""
    return hashlib.sha256(data.encode()).hexdigest()
