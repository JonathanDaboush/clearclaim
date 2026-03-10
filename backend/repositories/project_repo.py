# ProjectRepository for PostgreSQL
class ProjectRepository:
    @staticmethod
    def insert_project(name: str, main_party_id: str, created_at: str):
        """
        Insert project record.
        Args:
            name (str): Project name
            main_party_id (str): Main party user ID
            created_at (str): UTC timestamp
        Returns:
            str: Project ID
        """
        pass

    @staticmethod
    def delete_project(project_id: str):
        """
        Delete project record.
        Args:
            project_id (str): Project ID
        Returns:
            bool: Success
        """
        pass
