# KeySchema for serialization and type checking
from pydantic import BaseModel

class KeySchema(BaseModel):
    id: str
    user_id: str
    key_data: str
    created_at: str
