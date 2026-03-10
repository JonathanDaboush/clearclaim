# ContractRevisionApproval model
class ContractRevisionApproval:
    def __init__(self, id, contract_version_id, user_id, approved_at):
        self.id = id
        self.contract_version_id = contract_version_id
        self.user_id = user_id
        self.approved_at = approved_at
