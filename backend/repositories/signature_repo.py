import uuid
from typing import List, Set, Optional
from models.signature_model import Signature


class SignatureRepository:
    _signatures: List[Signature] = []  # In-memory (replace with DB in production)

    @staticmethod
    def insert_signature(contract_version_id: str, user_id: str, device_id: str, signed_at: str, signature_data: str = "", image_url: Optional[str] = None, ip: str = "") -> str:
        """Record a cryptographic signature event. Returns the new signature ID."""
        signature_id = str(uuid.uuid4())
        SignatureRepository._signatures.append(Signature(
            id=signature_id,
            contract_version_id=contract_version_id,
            user_id=user_id,
            device_id=device_id,
            signed_at=signed_at,
            signature_data=signature_data,
            image_url=image_url,
            ip=ip,
        ))
        return signature_id

    @staticmethod
    def delete_signature(signature_id: str) -> bool:
        """Remove a signature record. Returns True if found."""
        for sig in SignatureRepository._signatures:
            if sig.id == signature_id:
                SignatureRepository._signatures.remove(sig)
                return True
        return False

    @staticmethod
    def get_by_version_ids(version_ids: Set[str]) -> List[Signature]:
        """Return all signatures for the given set of contract version IDs."""
        return [s for s in SignatureRepository._signatures if s.contract_version_id in version_ids]
