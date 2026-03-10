# NotificationSchema for serialization and type checking
from pydantic import BaseModel
from typing import Optional

class NotificationSchema(BaseModel):
    id: str
    user_id: str
    event_type: str
    content: str
    related_object_id: str
    related_object_type: str
    sent_at: str
