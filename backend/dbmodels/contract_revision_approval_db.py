# ContractRevisionApproval DB model
class ContractRevisionApprovalDB:
    def __init__(self, id: str, contract_version_id: str, user_id: str, approved_at: str):
        self.id = id
        self.contract_version_id = contract_version_id
        self.user_id = user_id
        self.approved_at = approved_at
