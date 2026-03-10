# Subgroup model
class Subgroup:
    def __init__(self, id: str, project_id: str, name: str):
        """
        Subgroup entity.
        Args:
            id (str): Subgroup ID
            project_id (str): Project ID
            name (str): Subgroup name
        """
        self.id = id
        self.project_id = project_id
        self.name = name
