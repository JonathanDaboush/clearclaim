import uuid
from typing import Any, Dict, List
import db


class DevicesRepository:

    @staticmethod
    def add_device(user_id: str, device_info: str) -> str:
        device_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO devices (id, user_id, device_info) VALUES (%s, %s, %s)",
            (device_id, user_id, device_info),
        )
        return device_id

    @staticmethod
    def mark_trusted(device_id: str) -> bool:
        rows = db.query("SELECT id FROM devices WHERE id = %s AND revoked = FALSE", (device_id,))
        if not rows:
            return False
        db.execute("UPDATE devices SET trusted = TRUE WHERE id = %s", (device_id,))
        return True

    @staticmethod
    def revoke_device(device_id: str) -> bool:
        rows = db.query("SELECT id FROM devices WHERE id = %s AND revoked = FALSE", (device_id,))
        if not rows:
            return False
        db.execute("UPDATE devices SET revoked = TRUE, trusted = FALSE WHERE id = %s", (device_id,))
        return True

    @staticmethod
    def get_by_user(user_id: str) -> List[Dict[str, Any]]:
        return db.query(
            "SELECT id, user_id, device_info, trusted, added_at::text AS added_at, revoked FROM devices WHERE user_id = %s ORDER BY added_at",
            (user_id,),
        )

    @staticmethod
    def is_trusted(device_id: str) -> bool:
        rows = db.query("SELECT trusted FROM devices WHERE id = %s AND revoked = FALSE", (device_id,))
        return bool(rows and rows[0]["trusted"])
