# ContractService handles contract, revision, export, and evidence approval logic
class ContractService:
    def create_contract(self, project_id, created_by, content):
        """Create new contract."""
        pass

    def create_contract_revision(self, contract_id, new_content, user_id):
        """Create contract revision."""
        pass

    def generate_contract_diff(self, old_content, new_content):
        """Generate contract diff."""
        pass

    def approve_contract_revision(self, contract_version_id, user_id):
        """Approve contract revision."""
        pass

    def check_revision_unanimous_approval(self, contract_version_id):
        """Check if revision is unanimously approved."""
        pass

    def activate_contract_version(self, contract_version_id):
        """Activate contract version."""
        pass

    def get_contract_state(self, contract_id):
        """Get contract state."""
        pass

    def transition_contract_state(self, contract_id, new_state):
        """Transition contract to new state."""
        pass

    def get_contract_versions(self, contract_id):
        """Get all contract versions."""
        pass
