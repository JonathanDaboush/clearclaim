# Contract model
class Contract:
    def __init__(self, id, project_id, current_version_id, created_by):
        """
        Contract entity.
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
