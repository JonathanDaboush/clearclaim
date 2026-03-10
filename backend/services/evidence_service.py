# EvidenceService handles evidence file and approval logic
class EvidenceService:
    def upload_evidence(self, contract_id, file, user_id):
        """Upload evidence file for contract."""
        pass

    def validate_evidence_file(self, file):
        """Validate evidence file."""
        pass

    def calculate_evidence_hash(self, file):
        """Calculate hash of evidence file."""
        pass

    def store_evidence_file(self, file):
        """Store evidence file."""
        pass

    def propose_evidence_addition(self, contract_id, evidence_id, user_id):
        """Propose evidence addition for approval."""
        pass

    def approve_evidence(self, evidence_id, user_id):
        """Approve evidence addition."""
        pass

    def check_evidence_unanimous_approval(self, evidence_id):
        """Check if evidence addition is unanimously approved."""
        pass

    def activate_evidence(self, evidence_id):
        """Activate evidence after approval."""
        pass

    def request_evidence_deletion(self, evidence_id, user_id):
        """Request evidence deletion."""
        pass

    def approve_evidence_deletion(self, evidence_id, user_id):
        """Approve evidence deletion."""
        pass

    def delete_evidence(self, evidence_id):
        """Delete evidence file."""
        pass

    def get_contract_evidence(self, contract_id):
        """Get all evidence for contract."""
        pass
