import jwt
from typing import Optional

class User:
    def __init__(self, id: str, email: str, password_hash: str, authenticator_enabled: bool, role_id: Optional[str], verification_status: str, totp_secret: str = ""):
        """
        User entity.
        Args:
            id (str): User ID
            email (str): Email address
            password_hash (str): Hashed password
            authenticator_enabled (bool): 2FA enabled
            role_id (str): Role identifier
            verification_status (str): Verification state
            totp_secret (str): TOTP shared secret for 2FA
        """
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.authenticator_enabled = authenticator_enabled
        self.role_id = role_id
        self.verification_status = verification_status
        self.totp_secret = totp_secret

    def validate_email(self, email: str) -> bool:
        """
        Validate email format.
        Returns True if valid, else False.
        """
        import re
        return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None

    def generate_auth_token(self, user_id: str) -> str:
        """
        Generate authentication token for user.
        Returns a JWT token (stub).
        """
        return jwt.encode({'user_id': user_id}, 'secret', algorithm='HS256')  # type: ignore[reportUnknownMemberType]
