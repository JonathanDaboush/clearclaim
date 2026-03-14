import uuid
import datetime
from typing import Any, Dict, List, Optional
import db
from models.notification_model import Notification

_MAX_RETRIES = 3


class NotificationRepository:

    @staticmethod
    def insert_notification(
        user_id: str,
        event_type: str,
        content: str,
        related_object_id: str,
        related_object_type: str,
        sent_at: str,
    ) -> str:
        notification_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO notifications "
            "(id, user_id, event_type, content, related_object_id, related_object_type, sent_at, delivery_status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')",
            (notification_id, user_id, event_type, content, related_object_id, related_object_type, sent_at),
        )
        return notification_id

    @staticmethod
    def mark_delivered(notification_id: str) -> None:
        db.execute(
            "UPDATE notifications SET delivery_status = 'delivered', last_attempt_at = %s WHERE id = %s",
            (datetime.datetime.now(datetime.timezone.utc).isoformat(), notification_id),
        )

    @staticmethod
    def mark_failed(notification_id: str) -> None:
        """Increment retry_count; mark as 'failed' when max retries are exhausted."""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        db.execute(
            """
            UPDATE notifications
            SET retry_count      = retry_count + 1,
                last_attempt_at  = %s,
                delivery_status  = CASE
                    WHEN retry_count + 1 >= %s THEN 'failed'
                    ELSE 'retrying'
                END
            WHERE id = %s
            """,
            (now, _MAX_RETRIES, notification_id),
        )

    @staticmethod
    def get_pending_retries(limit: int = 50) -> List[Dict[str, Any]]:
        """Return notifications that should be retried (status = 'retrying')."""
        return db.query(
            "SELECT id, user_id, event_type, content FROM notifications "
            "WHERE delivery_status = 'retrying' AND retry_count < %s "
            "ORDER BY last_attempt_at ASC LIMIT %s",
            (_MAX_RETRIES, limit),
        )

    @staticmethod
    def mark_read(notification_id: str) -> bool:
        rows = db.query("SELECT id FROM notifications WHERE id = %s AND read_at IS NULL", (notification_id,))
        if not rows:
            return False
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        db.execute("UPDATE notifications SET read_at = %s WHERE id = %s", (now, notification_id))
        return True

    @staticmethod
    def delete_notification(notification_id: str) -> bool:
        rows = db.query("SELECT id FROM notifications WHERE id = %s", (notification_id,))
        if not rows:
            return False
        db.execute("DELETE FROM notifications WHERE id = %s", (notification_id,))
        return True

    @staticmethod
    def get_by_user(user_id: str) -> List[Notification]:
        rows = db.query(
            "SELECT id, user_id, event_type, content, related_object_id, related_object_type, sent_at, read_at FROM notifications WHERE user_id = %s ORDER BY sent_at DESC",
            (user_id,),
        )
        return [
            Notification(
                id=r["id"],
                user_id=r["user_id"],
                event_type=r["event_type"],
                content=r["content"],
                related_object_id=r["related_object_id"],
                related_object_type=r["related_object_type"],
                sent_at=r["sent_at"],
                read_at=r.get("read_at"),
            )
            for r in rows
        ]
