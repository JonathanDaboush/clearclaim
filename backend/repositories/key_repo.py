import uuid
import datetime
from typing import List, Optional
from models.key_model import Key, KEY_STATUS_ROTATED


class KeyRepository:
    _keys: List[Key] = []  # In-memory (replace with DB in production)

    @staticmethod
    def insert_key(key_type: str, parent_id: Optional[str] = None) -> str:
        """Store a key record in the hierarchy. Returns the new key ID."""
        key_id = str(uuid.uuid4())
        KeyRepository._keys.append(Key(
            id=key_id,
            type=key_type,
            created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            parent_id=parent_id,
        ))
        return key_id

    @staticmethod
    def rotate_key(key_id: str) -> Optional[str]:
        """Mark a key as rotated and return a new key ID signed by the old key.
        Per specs: key rotation supported, signed by previous keys."""
        for key in KeyRepository._keys:
            if key.id == key_id and key.status == "active":
                key.status = KEY_STATUS_ROTATED
                key.rotated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
                new_key_id = KeyRepository.insert_key(key.type, parent_id=key_id)
                return new_key_id
        return None

    @staticmethod
    def delete_key(key_id: str) -> bool:
        """Remove a key record. Returns True if found and deleted."""
        for key in KeyRepository._keys:
            if key.id == key_id:
                KeyRepository._keys.remove(key)
                return True
        return False

    @staticmethod
    def get_active_keys_by_type(key_type: str) -> List[Key]:
        """Return all active keys of a given type."""
        return [k for k in KeyRepository._keys if k.type == key_type and k.status == "active"]
