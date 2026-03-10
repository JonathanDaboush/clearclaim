# EvidenceDB for persistence mapping
    def __init__(self, id, contract_id, added_by, file_url, file_type=None, file_size=None, hash_value=None, metadata=None, integrity_verified=False):
        """
        Persistence model for DB operations.
        Args:
            id (str): Evidence ID
            contract_id (str): Contract ID
            added_by (str): User ID
            file_url (str): URL to evidence file
            file_type (str): File type
            file_size (int): File size
            hash_value (str): File hash
            metadata (dict): Evidence metadata
            integrity_verified (bool): Integrity check
        """
        self.id = id
        self.contract_id = contract_id
        self.added_by = added_by
        self.file_url = file_url
        self.file_type = file_type
        self.file_size = file_size
        self.hash_value = hash_value
        self.metadata = metadata
        self.integrity_verified = integrity_verified
