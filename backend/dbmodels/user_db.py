# UserDB for persistence mapping
class UserDB:
    def __init__(self, id, email, password_hash, authenticator_enabled, role_id, verification_status):
        """
        Persistence model for DB operations.
        Args:
            id (str): User ID
            email (str): Email address
            password_hash (str): Hashed password
            authenticator_enabled (bool): 2FA enabled
            role_id (str): Role identifier
            verification_status (str): Verification state
        """
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.authenticator_enabled = authenticator_enabled
        self.role_id = role_id
        self.verification_status = verification_status
