# SignatureSchema for serialization and type checking
from pydantic import BaseModel

class SignatureSchema(BaseModel):
    id: str
    contract_version_id: str
    user_id: str
    device_id: str
    signed_at: str
