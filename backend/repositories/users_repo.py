# UsersRepository for PostgreSQL
class UsersRepository:
    @staticmethod
    def create_user(email: str, password_hash: str):
        """
        Insert user in DB.
        Args:
            email (str): Email
            password_hash (str): Hashed password
        Returns:
            str: User ID
        """
        pass

    @staticmethod
    def get_user_by_email(email: str):
        """
        Fetch user by email.
        Args:
            email (str): Email
        Returns:
            User: User object
        """
        pass
