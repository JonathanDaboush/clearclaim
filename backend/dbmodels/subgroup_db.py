# SubgroupDB for persistence mapping
class SubgroupDB:
    def __init__(self, id, project_id, name):
        """
        Persistence model for DB operations.
        Args:
            id (str): Subgroup ID
            project_id (str): Project ID
            name (str): Subgroup name
        """
        self.id = id
        self.project_id = project_id
        self.name = name
