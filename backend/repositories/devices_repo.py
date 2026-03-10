import uuid
import datetime
from typing import List, Dict, Any


class DevicesRepository:
    _devices: List[Dict[str, Any]] = []  # In-memory (replace with DB in production)

    @staticmethod
    def add_device(user_id: str, device_info: str) -> str:
        """Register a new device for a user as untrusted pending verification. Returns its ID."""
        device_id = str(uuid.uuid4())
        DevicesRepository._devices.append({
            "id": device_id,
            "user_id": user_id,
            "device_info": device_info,
            "trusted": False,  # Must pass authenticator + email verification before trusted
            "added_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "revoked": False,
        })
        return device_id

    @staticmethod
    def mark_trusted(device_id: str) -> bool:
        """Mark a device as trusted after authenticator + email verification. Returns True if found."""
        for device in DevicesRepository._devices:
            if device["id"] == device_id and not device["revoked"]:
                device["trusted"] = True
                return True
        return False

    @staticmethod
    def revoke_device(device_id: str) -> bool:
        """Revoke a device so it can no longer sign or authenticate. Returns True if found."""
        for device in DevicesRepository._devices:
            if device["id"] == device_id and not device["revoked"]:
                device["revoked"] = True
                device["trusted"] = False
                return True
        return False

    @staticmethod
    def get_by_user(user_id: str) -> List[Dict[str, Any]]:
        """Return all device records for a given user."""
        return [d for d in DevicesRepository._devices if d["user_id"] == user_id]

    @staticmethod
    def is_trusted(device_id: str) -> bool:
        """Return True if the device is registered, trusted, and not revoked."""
        for device in DevicesRepository._devices:
            if device["id"] == device_id:
                return bool(device["trusted"] and not device["revoked"])
        return False
