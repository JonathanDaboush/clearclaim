from typing import Optional

# SignatureDB for persistence mapping
class SignatureDB:
    def __init__(self, id: str, contract_version_id: str, user_id: str, device_id: str, signed_at: str, signature_data: str = "", image_url: Optional[str] = None, ip: str = ""):
        """
        Persistence model for DB operations.
        Args:
            id (str): Signature ID
            contract_version_id (str): Contract version ID
            user_id (str): User ID
            device_id (str): Device ID
            signed_at (str): UTC timestamp
            signature_data (str): Cryptographic signature hash
            image_url (str): Optional stored signature image URL
            ip (str): IP address of signing device
        """
        self.id = id
        self.contract_version_id = contract_version_id
        self.user_id = user_id
        self.device_id = device_id
        self.signed_at = signed_at
        self.signature_data = signature_data
        self.image_url = image_url
        self.ip = ip
