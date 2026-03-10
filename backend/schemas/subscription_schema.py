# SubscriptionSchema for serialization and type checking
from pydantic import BaseModel

class SubscriptionSchema(BaseModel):
    id: str
    user_id: str
    tier: str
    start_date: str
    end_date: str
