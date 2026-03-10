# RevisionChange model
class RevisionChange:
    def __init__(self, id, contract_version_id, change_type, change_data):
        """Revision change entity."""
        self.id = id
        self.contract_version_id = contract_version_id
        self.change_type = change_type
        self.change_data = change_data
