# ProjectSchema for serialization and type checking
from pydantic import BaseModel
from typing import Optional

class ProjectSchema(BaseModel):
    id: str
    name: str
    main_party_id: str
    created_at: str
    deleted_at: Optional[str]
