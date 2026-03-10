import uuid
from typing import List, Dict, Any, Optional
from models.user_model import User


class UsersRepository:
    _users: List[User] = []  # In-memory (replace with DB in production)
    _reset_tokens: Dict[str, str] = {}  # token -> user_id

    @staticmethod
    def create_user(email: str, password_hash: str) -> str:
        """Create a new user record. Returns the new user ID."""
        user_id = str(uuid.uuid4())
        UsersRepository._users.append(User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            authenticator_enabled=False,
            role_id=None,
            verification_status="unverified",
        ))
        return user_id

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Fetch a user by email address. Returns a dict or None."""
        for user in UsersRepository._users:
            if user.email == email:
                return {
                    "id": user.id,
                    "email": user.email,
                    "password_hash": user.password_hash,
                    "role_id": user.role_id,
                    "verification_status": user.verification_status,
                }
        return None

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a user by ID. Returns a dict or None."""
        for user in UsersRepository._users:
            if user.id == user_id:
                return {
                    "id": user.id,
                    "email": user.email,
                    "role_id": user.role_id,
                    "verification_status": user.verification_status,
                }
        return None

    @staticmethod
    def update_password(user_id: str, new_hash: str) -> bool:
        """Update the stored password hash for a user. Returns True if found."""
        for user in UsersRepository._users:
            if user.id == user_id:
                user.password_hash = new_hash
                return True
        return False

    @staticmethod
    def delete_user(user_id: str) -> bool:
        """Remove a user record (account deletion). Returns True if found.
        Note: audit logs and evidence are preserved for legal compliance."""
        for user in UsersRepository._users:
            if user.id == user_id:
                UsersRepository._users.remove(user)
                return True
        return False

    @staticmethod
    def store_reset_token(token: str, user_id: str) -> None:
        """Store a password-reset token mapped to the user's ID."""
        UsersRepository._reset_tokens[token] = user_id

    @staticmethod
    def consume_reset_token(token: str) -> Optional[str]:
        """Validate and consume a reset token. Returns user_id or None if invalid."""
        return UsersRepository._reset_tokens.pop(token, None)
