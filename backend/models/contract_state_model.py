# ContractState model
class ContractState:
    def __init__(self, contract_id: str, state: str, updated_at: str):
        self.contract_id = contract_id
        self.state = state
        self.updated_at = updated_at
