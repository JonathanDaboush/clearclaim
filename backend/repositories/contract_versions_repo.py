# ContractVersionsRepository for PostgreSQL
class ContractVersionsRepository:
    @staticmethod
    def create_contract_version(contract_id: str, content: str, created_by: str):
        """
        Create contract version.
        Args:
            contract_id (str): Contract ID
            content (str): Contract content
            created_by (str): User ID
        Returns:
            str: Version ID
        """
        pass

    @staticmethod
    def add_approval(contract_version_id: str, user_id: str):
        """
        Add approval to contract version.
        Args:
            contract_version_id (str): Version ID
            user_id (str): User ID
        Returns:
            bool: Success
        """
        pass

    @staticmethod
    def check_unanimous(contract_version_id: str) -> bool:
        """
        Check if all required users approved.
        Args:
            contract_version_id (str): Version ID
        Returns:
            bool: Unanimous
        """
        pass

    @staticmethod
    def mark_signed(contract_version_id: str):
        """
        Mark contract version as signed.
        Args:
            contract_version_id (str): Version ID
        Returns:
            bool: Success
        """
        pass
