# Device model
class Device:
    def __init__(self, id, user_id, device_name, trusted, created_at, revoked_at):
        self.id = id
        self.user_id = user_id
        self.device_name = device_name
        self.trusted = trusted
        self.created_at = created_at
        self.revoked_at = revoked_at
