# SignatureRepository for PostgreSQL
class SignatureRepository:
    @staticmethod
    def insert_signature(contract_version_id: str, user_id: str, device_id: str, signed_at: str):
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

    @staticmethod
    def delete_signature(signature_id: str):
        """
        Delete signature record.
        Args:
            signature_id (str): Signature ID
        Returns:
            bool: Success
        """
        pass
