# Device model
class Device:
    def __init__(self, id: str, user_id: str, device_name: str, trusted: bool, created_at: str, revoked_at: str):
        self.id = id
        self.user_id = user_id
        self.device_name = device_name
        self.trusted = trusted
        self.created_at = created_at
        self.revoked_at = revoked_at
