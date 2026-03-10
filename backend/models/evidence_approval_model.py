# EvidenceApproval model
class EvidenceApproval:
    def __init__(self, id, evidence_id, user_id, approved_at):
        """Evidence approval entity."""
        self.id = id
        self.evidence_id = evidence_id
        self.user_id = user_id
        self.approved_at = approved_at
