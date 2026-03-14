# Device DB model
class DeviceDB:
    def __init__(
        self,
        id: str,
        user_id: str,
        device_name: str,
        trusted: bool,
        created_at: str,
        revoked_at: str | None = None,
        device_fingerprint: str = '',
        last_seen: str | None = None,
        risk_score: int = 0,
    ):
        self.id = id
        self.user_id = user_id
        self.device_name = device_name
        self.trusted = trusted
        self.created_at = created_at
        self.revoked_at = revoked_at
        self.device_fingerprint = device_fingerprint
        self.last_seen = last_seen
        self.risk_score = risk_score
