import uuid
import datetime
from typing import List, Dict, Any
from models.identity_verification_model import IdentityVerification


class IdentityRepository:
    _verifications: List[IdentityVerification] = []  # In-memory (replace with DB in production)

    def create_verification(self, user_id: str, provider: str, status: str) -> str:
        """Create an identity verification record. Returns the new verification ID."""
        verification_id = str(uuid.uuid4())
        verification = IdentityVerification(
            id=verification_id,
            user_id=user_id,
            provider=provider,
            status=status,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )
        self._verifications.append(verification)
        return verification_id

    def get_verification(self, user_id: str) -> Dict[str, Any]:
        """Return the identity verification record for a user, or not_verified."""
        for v in self._verifications:
            if v.user_id == user_id:
                return {"id": v.id, "user_id": v.user_id, "provider": v.provider, "status": v.status, "timestamp": v.timestamp}
        return {"status": "not_verified"}

    def update_verification(self, user_id: str, status: str) -> bool:
        """Update the verification status for a user. Returns True if found."""
        for v in self._verifications:
            if v.user_id == user_id:
                v.status = status
                v.timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
                return True
        return False
