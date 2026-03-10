# ContractVersionSchema for serialization and type checking
from pydantic import BaseModel

class ContractVersionSchema(BaseModel):
    id: str
    contract_id: str
    content: str
    created_by: str
    signed: bool
    created_at: str
