import uuid
import datetime
from typing import Any, Dict, List, Optional
import db
from models.key_model import Key, KEY_STATUS_ROTATED


class KeyRepository:

    @staticmethod
    def insert_key(key_type: str, parent_id: Optional[str] = None) -> str:
        # Enforce key hierarchy: system keys must have a root parent; session keys must have a system parent
        if key_type == 'system' and parent_id:
            parent_rows = db.query("SELECT type FROM keys WHERE id = %s AND status = 'active'", (parent_id,))
            if not parent_rows or parent_rows[0]['type'] != 'root':
                raise ValueError("A system key's parent must be an active root key.")
        elif key_type == 'session' and parent_id:
            parent_rows = db.query("SELECT type FROM keys WHERE id = %s AND status = 'active'", (parent_id,))
            if not parent_rows or parent_rows[0]['type'] != 'system':
                raise ValueError("A session key's parent must be an active system key.")
        key_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO keys (id, type, parent_id) VALUES (%s, %s, %s)",
            (key_id, key_type, parent_id),
        )
        return key_id

    @staticmethod
    def rotate_key(key_id: str) -> Optional[str]:
        rows = db.query("SELECT id, type FROM keys WHERE id = %s AND status = 'active'", (key_id,))
        if not rows:
            return None
        rotated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        db.execute(
            "UPDATE keys SET status = %s, rotated_at = %s WHERE id = %s",
            (KEY_STATUS_ROTATED, rotated_at, key_id),
        )
        return KeyRepository.insert_key(rows[0]["type"], parent_id=key_id)

    @staticmethod
    def delete_key(key_id: str) -> bool:
        rows = db.query("SELECT id FROM keys WHERE id = %s", (key_id,))
        if not rows:
            return False
        db.execute("DELETE FROM keys WHERE id = %s", (key_id,))
        return True

    @staticmethod
    def get_active_keys_by_type(key_type: str) -> List[Key]:
        rows = db.query(
            "SELECT id, type, created_at::text AS created_at, parent_id, status, rotated_at::text AS rotated_at FROM keys WHERE type = %s AND status = 'active'",
            (key_type,),
        )
        result = []
        for r in rows:
            k = Key(
                id=r["id"],
                type=r["type"],
                created_at=r["created_at"],
                parent_id=r.get("parent_id"),
                rotated_at=r.get("rotated_at"),
            )
            result.append(k)
        return result
