import uuid


class SignatureSQL:
    def insert_signature(self, contract_version_id: str, user_id: str, device_id: str, signed_at: str) -> str:
        """Return the SQL insert values for a signature record. Returns new signature ID."""
        return str(uuid.uuid4())  # In production: delegate to SQLTemplate.insert(...)
