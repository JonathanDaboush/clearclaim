# SignatureSQL class for signature DB operations
class SignatureSQL:
    def insert_signature(self, contract_version_id: str, user_id: str, device_id: str, signed_at: str) -> str:
        """
        Insert signature record.
        Args:
            contract_version_id (str): Contract version ID
            user_id (str): User ID
            device_id (str): Device ID
            signed_at (str): UTC timestamp
        Returns:
            str: Signature ID
        """
        pass
