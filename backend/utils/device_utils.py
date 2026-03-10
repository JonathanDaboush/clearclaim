import hashlib
from repositories.devices_repo import DevicesRepository
from repositories.audit_repo import AuditRepository


def generate_device_identifier(device_info: str) -> str:
    """Return a deterministic device ID from the device_info fingerprint."""
    return hashlib.sha256(device_info.encode()).hexdigest()


def verify_device_trust(user_id: str, device_id: str) -> bool:
    """Return True if the device is registered to the user and is trusted."""
    for device in DevicesRepository.get_by_user(user_id):
        if device["id"] == device_id:
            return DevicesRepository.is_trusted(device_id)
    return False


def record_device_login(user_id: str, device_id: str):
    """Append a device login event to the audit log."""
    AuditRepository.log_event(
        user_id=user_id,
        device_id=device_id,
        event_type="device_login",
        details="Device login recorded.",
    )


def revoke_device_access(device_id: str) -> bool:
    """Revoke a device and record the revocation in the audit log."""
    revoked = DevicesRepository.revoke_device(device_id)
    if revoked:
        AuditRepository.log_event(
            user_id="",
            device_id=device_id,
            event_type="device_revoked",
            details="Device access revoked.",
        )
    return revoked
