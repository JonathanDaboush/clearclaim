import uuid
from typing import Any, Dict, List, Optional
import db
from utils.security_utils import generate_totp_secret


class UsersRepository:

    @staticmethod
    def create_user(email: str, password_hash: str) -> Dict[str, str]:
        user_id = str(uuid.uuid4())
        totp_secret = generate_totp_secret()
        db.execute(
            "INSERT INTO users (id, email, password_hash, totp_secret) VALUES (%s, %s, %s, %s)",
            (user_id, email, password_hash, totp_secret),
        )
        return {"user_id": user_id, "totp_secret": totp_secret}

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        rows = db.query(
            "SELECT id, email, password_hash, role_id, verification_status, totp_secret FROM users WHERE email = %s",
            (email,),
        )
        return rows[0] if rows else None

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        rows = db.query(
            "SELECT id, email, role_id, verification_status, totp_secret FROM users WHERE id = %s",
            (user_id,),
        )
        return rows[0] if rows else None

    @staticmethod
    def update_password(user_id: str, new_hash: str) -> bool:
        db.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))
        return True

    @staticmethod
    def delete_user(user_id: str) -> bool:
        rows = db.query("SELECT id FROM users WHERE id = %s", (user_id,))
        if not rows:
            return False
        db.execute("DELETE FROM users WHERE id = %s", (user_id,))
        return True

    @staticmethod
    def store_reset_token(token: str, user_id: str) -> None:
        db.execute(
            "INSERT INTO password_reset_tokens (token, user_id) VALUES (%s, %s) ON CONFLICT (token) DO NOTHING",
            (token, user_id),
        )

    @staticmethod
    def consume_reset_token(token: str) -> Optional[str]:
        rows = db.query("SELECT user_id FROM password_reset_tokens WHERE token = %s", (token,))
        if not rows:
            return None
        user_id = rows[0]["user_id"]
        db.execute("DELETE FROM password_reset_tokens WHERE token = %s", (token,))
        return user_id
