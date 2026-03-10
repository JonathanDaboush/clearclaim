# Signature model
class Signature:
    def __init__(self, id, contract_version_id, user_id, device_id, signed_at):
        """
        Signature entity.
        Args:
            id (str): Signature ID
            contract_version_id (str): Contract version ID
            user_id (str): User ID
            device_id (str): Device ID
            signed_at (str): UTC timestamp
        """
        self.id = id
        self.contract_version_id = contract_version_id
        self.user_id = user_id
        self.device_id = device_id
        self.signed_at = signed_at
