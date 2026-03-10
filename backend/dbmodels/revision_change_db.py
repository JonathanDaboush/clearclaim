# RevisionChange DB model
class RevisionChangeDB:
    def __init__(self, id: str, contract_version_id: str, change_type: str, change_data: str):
        self.id = id
        self.contract_version_id = contract_version_id
        self.change_type = change_type
        self.change_data = change_data
