# IdentityVerification DB model
class IdentityVerificationDB:
    def __init__(self, id: str, user_id: str, provider: str, status: str, timestamp: str):
        self.id = id
        self.user_id = user_id
        self.provider = provider
        self.status = status
        self.timestamp = timestamp
