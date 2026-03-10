# Key model
class Key:
    def __init__(self, id, user_id, key_data, created_at):
        """
        Key entity.
        Args:
            id (str): Key ID
            user_id (str): User ID
            key_data (str): Key data
            created_at (str): UTC timestamp
        """
        self.id = id
        self.user_id = user_id
        self.key_data = key_data
        self.created_at = created_at
