import datetime
from typing import List, Dict, Any
from repositories.notification_repo import NotificationRepository


class NotificationService:
    def create_notification(self, user_id: str, event_type: str, content: str, related_object_id: str = '') -> Dict[str, Any]:
        """Create and store a notification. Routes certain event types to email."""
        sent_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        notification_id = NotificationRepository.insert_notification(
            user_id=user_id,
            event_type=event_type,
            content=content,
            related_object_id=related_object_id,
            related_object_type="",
            sent_at=sent_at,
        )
        # Events that warrant an email in addition to in-app notification
        _EMAIL_EVENTS = {
            "breach", "parental_consent", "consent", "accessibility",
            "invited", "password_reset", "signature_request",
            "new_device_login", "revision_created", "evidence_uploaded",
        }
        try:
            if event_type in _EMAIL_EVENTS:
                subject = {
                    "breach": "Security Alert — ClearClaim",
                    "invited": "You've been invited to a project — ClearClaim",
                    "password_reset": "Password Reset — ClearClaim",
                    "signature_request": "Signature Required — ClearClaim",
                    "new_device_login": "New Device Login — ClearClaim",
                    "revision_created": "Contract Revision Pending — ClearClaim",
                    "evidence_uploaded": "New Evidence Added — ClearClaim",
                }.get(event_type, event_type.replace("_", " ").title() + " — ClearClaim")
                self._send_email_with_tracking(notification_id, user_id, subject, content)
            else:
                self._deliver_in_app(notification_id)
        except Exception:
            NotificationRepository.mark_failed(notification_id)
        return {"status": "Notification created", "notification_id": notification_id}

    def _send_email_with_tracking(self, notification_id: str, user_id: str, subject: str, message: str) -> None:
        from services.async_tasks import AsyncTasks
        try:
            AsyncTasks.send_email_async(user_id, subject, message, notification_id=notification_id)
            NotificationRepository.mark_delivered(notification_id)
        except Exception:
            NotificationRepository.mark_failed(notification_id)
            raise

    def _deliver_in_app(self, notification_id: str) -> None:
        """In-app notifications are already persisted; just mark them delivered."""
        NotificationRepository.mark_delivered(notification_id)

    def retry_failed_notifications(self) -> Dict[str, Any]:
        """Retry all notifications that are in 'retrying' state. Called by background worker."""
        pending = NotificationRepository.get_pending_retries()
        retried = 0
        for row in pending:
            try:
                from services.async_tasks import AsyncTasks
                AsyncTasks.send_email_async(
                    row["user_id"],
                    row["event_type"].replace("_", " ").title(),
                    row["content"],
                    notification_id=row["id"],
                )
                NotificationRepository.mark_delivered(row["id"])
                retried += 1
            except Exception:
                NotificationRepository.mark_failed(row["id"])
        return {"retried": retried}

    def resolve_notification_recipients(self, event_type: str, project_id: str) -> List[str]:
        from utils.notification_recipient_resolver import NotificationRecipientResolver
        return NotificationRecipientResolver.resolve_recipients(project_id, event_type)

    def send_email_notification(self, user_id: str, subject: str, message: str):
        from services.async_tasks import AsyncTasks
        AsyncTasks.send_email_async(user_id, subject, message)

    def send_in_app_notification(self, user_id: str, message: str):
        pass  # Already persisted via NotificationRepository.insert_notification

    def mark_notification_read(self, notification_id: str) -> bool:
        return NotificationRepository.mark_read(notification_id)

    def get_user_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        notifications = NotificationRepository.get_by_user(user_id)
        return [
            {
                "id": n.id,
                "user_id": n.user_id,
                "type": n.event_type,
                "message": n.content,
                "is_read": n.read_at is not None,
                "created_at": n.sent_at,
                "related_object_id": getattr(n, "related_object_id", "") or "",
            }
            for n in notifications
        ]
