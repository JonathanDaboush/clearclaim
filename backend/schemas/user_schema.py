# UserSchema for serialization and type checking
from pydantic import BaseModel
from typing import Optional

class UserSchema(BaseModel):
    id: str
    email: str
    password_hash: str
    authenticator_enabled: bool
    role_id: str
    verification_status: str
