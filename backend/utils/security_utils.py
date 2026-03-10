import hashlib
import hmac
import secrets
import pyotp as _pyotp  # type: ignore[import-untyped]
from typing import Any, cast

pyotp = cast(Any, _pyotp)


def hash_password(password: str) -> str:
    """Return a SHA-256 hash of the password. Use bcrypt/argon2 in production."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Return True if hash_password(password) matches the stored hash."""
    return hmac.compare_digest(hash_password(password), password_hash)


def generate_totp_secret() -> str:
    """Generate a new Base32 TOTP secret key."""
    return pyotp.random_base32()


def verify_totp(secret: str, code: str) -> bool:
    """Return True if the TOTP code is valid for the given secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)


def generate_secure_token() -> str:
    """Return a cryptographically secure random hex token."""
    return secrets.token_hex(32)


def hash_data(data: str) -> str:
    """Return a SHA-256 hash of the given data string."""
    return hashlib.sha256(data.encode()).hexdigest()
