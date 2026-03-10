# ContractRevisionApprovalRepository handles revision approval persistence
class ContractRevisionApprovalRepository:
    def create_approval(self, contract_version_id, user_id):
        """Create revision approval record."""
        pass

    def get_approval(self, contract_version_id, user_id):
        """Get revision approval for user."""
        pass

    def get_approvals_for_version(self, contract_version_id):
        """Get all approvals for contract version."""
        pass
