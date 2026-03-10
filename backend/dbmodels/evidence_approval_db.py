# EvidenceApproval DB model
class EvidenceApprovalDB:
    def __init__(self, id: str, evidence_id: str, user_id: str, approved_at: str):
        self.id = id
        self.evidence_id = evidence_id
        self.user_id = user_id
        self.approved_at = approved_at
