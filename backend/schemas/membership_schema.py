# MembershipSchema for serialization and type checking
from pydantic import BaseModel

class MembershipSchema(BaseModel):
    id: str
    user_id: str
    project_id: str
    subgroup_id: str
    role_id: str
