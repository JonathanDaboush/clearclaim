# KeyRepository for PostgreSQL
class KeyRepository:
    @staticmethod
    def insert_key(user_id: str, key_data: str, created_at: str):
        """
        Insert key record.
        Args:
            user_id (str): User ID
            key_data (str): Key data
            created_at (str): UTC timestamp
        Returns:
            str: Key ID
        """
        pass

    @staticmethod
    def delete_key(key_id: str):
        """
        Delete key record.
        Args:
            key_id (str): Key ID
        Returns:
            bool: Success
        """
        pass
