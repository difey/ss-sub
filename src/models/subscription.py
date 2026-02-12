from pydantic import BaseModel, Field
from typing import Optional
import uuid

class SubscriptionCreate(BaseModel):
    url: str
    name: Optional[str] = None

class Subscription(SubscriptionCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
