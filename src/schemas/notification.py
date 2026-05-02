from typing import Optional
from pydantic import BaseModel, UUID4
from datetime import datetime

class NotificationBase(BaseModel):
    title: str
    body: str
    type: str
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID4] = None

class NotificationCreate(NotificationBase):
    user_id: UUID4
    masjid_id: UUID4

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class NotificationRead(NotificationBase):
    id: UUID4
    user_id: UUID4
    masjid_id: UUID4
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
