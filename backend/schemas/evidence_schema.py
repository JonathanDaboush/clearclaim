# EvidenceSchema for serialization and type checking
from pydantic import BaseModel

class EvidenceSchema(BaseModel):
    id: str
    contract_id: str
    added_by: str
    file_url: str
    file_type: str = None
    file_size: int = None
    hash_value: str = None
    metadata: dict = None
    integrity_verified: bool = False
