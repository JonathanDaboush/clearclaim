# ContractVersion model
class ContractVersion:
    def __init__(self, id: str, contract_id: str, content: str, created_by: str, signed: bool, created_at: str):
        """
        Contract version entity.
        Args:
            id (str): Version ID
            contract_id (str): Contract ID
            content (str): Contract text
            created_by (str): User ID
            signed (bool): Signed status
            created_at (str): UTC timestamp
        """
        self.id = id
        self.contract_id = contract_id
        self.content = content
        self.created_by = created_by
        self.signed = signed
        self.created_at = created_at
