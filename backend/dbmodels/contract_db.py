# ContractDB for persistence mapping
class ContractDB:
    def __init__(self, id: str, project_id: str, current_version_id: str, created_by: str):
        """
        Persistence model for DB operations.
        Args:
            id (str): Contract ID
            project_id (str): Project ID
            current_version_id (str): Current contract version
            created_by (str): User ID
        """
        self.id = id
        self.project_id = project_id
        self.current_version_id = current_version_id
        self.created_by = created_by
