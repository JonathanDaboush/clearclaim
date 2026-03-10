# SubgroupSchema for serialization and type checking
from pydantic import BaseModel

class SubgroupSchema(BaseModel):
    id: str
    project_id: str
    name: str
