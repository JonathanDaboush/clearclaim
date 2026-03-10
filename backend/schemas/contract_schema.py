# ContractSchema for serialization and type checking
from pydantic import BaseModel

class ContractSchema(BaseModel):
    id: str
    project_id: str
    current_version_id: str
    created_by: str
