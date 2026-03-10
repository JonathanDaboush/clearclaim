import uuid


class Contract:
    def __init__(self, id: str, project_id: str, current_version_id: str, created_by: str):
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

    def validate_contract_content(self, content: str) -> bool:
        """
        Validate contract content.
        Returns True if content is not empty.
        """
        return bool(content and len(content.strip()) > 0)

    def generate_contract_version_id(self) -> str:
        """
        Generate unique contract version ID.
        Returns a UUID.
        """
        return str(uuid.uuid4())
