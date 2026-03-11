from typing import Optional

class Signature:
    def __init__(self, id: str, contract_version_id: str, user_id: str, device_id: str, signed_at: str, signature_hash: str = "", image_url: Optional[str] = None, ip: str = ""):
        """
        Signature entity.
        Args:
            id (str): Signature ID
            contract_version_id (str): Contract version ID
            user_id (str): User ID
            device_id (str): Device ID
            signed_at (str): UTC timestamp
            signature_hash (str): Cryptographic signature hash
            image_url (str): Optional stored signature image URL
            ip (str): IP address of signing device
        """
        self.id = id
        self.contract_version_id = contract_version_id
        self.user_id = user_id
        self.device_id = device_id
        self.signed_at = signed_at
        self.signature_hash = signature_hash
        self.image_url = image_url
        self.ip = ip

    def validate_signature(self, user_id: str, contract_version_id: str, device_id: str) -> bool:
        """
        Validate signature input.
        Args:
            user_id (str): User ID
            contract_version_id (str): Contract version ID
            device_id (str): Device ID
        Returns:
            bool: True if valid
        """
        return bool(user_id and contract_version_id and device_id)
