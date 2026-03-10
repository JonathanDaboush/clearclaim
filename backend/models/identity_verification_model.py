# IdentityVerification model
class IdentityVerification:
    def __init__(self, id, user_id, provider, status, timestamp):
        self.id = id
        self.user_id = user_id
        self.provider = provider
        self.status = status
        self.timestamp = timestamp
