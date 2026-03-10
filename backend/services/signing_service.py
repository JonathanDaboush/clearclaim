# SigningService handles contract signing logic
class SigningService:
    def request_signature(self, contract_version_id, user_id):
        """Request signature for contract version."""
        pass

    def verify_signing_totp(self, user_id, code):
        """Verify TOTP for signing."""
        pass

    def sign_contract(self, contract_version_id, user_id, device_id, ip):
        """Sign contract version."""
        pass

    def generate_signature_hash(self, contract_version_id, user_id):
        """Generate signature hash."""
        pass

    def store_signature(self, contract_version_id, user_id, device_id, ip):
        """Store signature record."""
        pass

    def get_contract_signatures(self, contract_version_id):
        """Get all signatures for contract version."""
        pass

    def check_contract_fully_signed(self, contract_version_id):
        """Check if contract version is fully signed."""
        pass
