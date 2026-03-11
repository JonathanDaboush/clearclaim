import uuid
import datetime
from typing import Any, Dict
import db


class IdentityVerificationRepository:

    def create_verification(self, user_id: str, provider: str, status: str) -> str:
        verification_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        db.execute(
            """
            INSERT INTO identity_verifications (id, user_id, provider, status, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
              SET provider = EXCLUDED.provider,
                  status   = EXCLUDED.status,
                  timestamp = EXCLUDED.timestamp
            """,
            (verification_id, user_id, provider, status, timestamp),
        )
        return verification_id

    def get_verification(self, user_id: str) -> Dict[str, Any]:
        rows = db.query(
            "SELECT id, user_id, provider, status, timestamp FROM identity_verifications WHERE user_id = %s",
            (user_id,),
        )
        return rows[0] if rows else {"status": "not_verified"}

    def update_verification(self, user_id: str, status: str) -> bool:
        rows = db.query("SELECT id FROM identity_verifications WHERE user_id = %s", (user_id,))
        if not rows:
            return False
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        db.execute(
            "UPDATE identity_verifications SET status = %s, timestamp = %s WHERE user_id = %s",
            (status, timestamp, user_id),
        )
        return True
