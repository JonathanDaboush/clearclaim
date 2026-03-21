import uuid
import datetime
from typing import Any, Dict, List
import db


class DevicesRepository:

    @staticmethod
    def add_device(user_id: str, device_info: str, location: str = '', device_fingerprint: str = '') -> str:
        device_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO devices (id, user_id, device_info, location, device_fingerprint) VALUES (%s, %s, %s, %s, %s)",
            (device_id, user_id, device_info, location, device_fingerprint),
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
        db.execute("UPDATE devices SET revoked = TRUE, trusted = FALSE, revoked_at = NOW() WHERE id = %s", (device_id,))
        return True

    @staticmethod
    def update_last_seen(device_id: str) -> None:
        """Stamp the device's last_seen timestamp on every authenticated request."""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        db.execute(
            "UPDATE devices SET last_seen = %s WHERE id = %s",
            (now, device_id),
        )

    @staticmethod
    def update_risk_score(device_id: str, score: int) -> None:
        """Set the calculated risk score on a device (0 = low, 100 = high risk)."""
        db.execute(
            "UPDATE devices SET risk_score = %s WHERE id = %s",
            (max(0, min(100, score)), device_id),
        )

    @staticmethod
    def get_by_user(user_id: str) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT d.id, d.user_id, d.device_info, d.location, d.trusted,
                   d.added_at::text AS added_at, d.revoked,
                   d.revoked_at::text AS revoked_at,
                   d.device_fingerprint, d.last_seen::text AS last_seen,
                   d.risk_score,
                   MAX(al.timestamp)::text AS last_activity
            FROM devices d
            LEFT JOIN audit_logs al ON al.device_id = d.id AND al.device_id != ''
            WHERE d.user_id = %s
            GROUP BY d.id, d.user_id, d.device_info, d.location, d.trusted,
                     d.added_at, d.revoked, d.revoked_at, d.device_fingerprint, d.last_seen, d.risk_score
            ORDER BY d.added_at
            """,
            (user_id,),
        )

    @staticmethod
    def is_trusted(device_id: str) -> bool:
        rows = db.query("SELECT trusted FROM devices WHERE id = %s AND revoked = FALSE", (device_id,))
        return bool(rows and rows[0]["trusted"])
