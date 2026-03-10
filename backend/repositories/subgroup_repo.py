# SubgroupRepository for PostgreSQL
class SubgroupRepository:
    @staticmethod
    def insert_subgroup(project_id: str, name: str):
        """
        Insert subgroup record.
        Args:
            project_id (str): Project ID
            name (str): Subgroup name
        Returns:
            str: Subgroup ID
        """
        pass

    @staticmethod
    def delete_subgroup(subgroup_id: str):
        """
        Delete subgroup record.
        Args:
            subgroup_id (str): Subgroup ID
        Returns:
            bool: Success
        """
        pass
