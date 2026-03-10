# AuditLogSchema for serialization and type checking
from pydantic import BaseModel
from typing import Optional

class AuditLogSchema(BaseModel):
    id: str
    user_id: str
    device_id: str
    event_type: str
    related_object_id: Optional[str]
    details: Optional[str]
    timestamp: str
    hash: str
