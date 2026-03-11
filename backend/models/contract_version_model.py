# ContractVersion model
class ContractVersion:
    def __init__(self, id: str, contract_id: str, content: str, created_by: str, signed: bool, created_at: str, version_number: int = 1, content_hash: str = ''):
        self.id = id
        self.contract_id = contract_id
        self.content = content
        self.created_by = created_by
        self.signed = signed
        self.created_at = created_at
        self.version_number = version_number
        self.content_hash = content_hash
