from typing import Optional, Dict
from sqlmodel import SQLModel
import uuid
from datetime import datetime

class AuditLogBase(SQLModel):
    masjid_id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    user_name: str
    action: str
    entity_type: str
    entity_id: Optional[uuid.UUID] = None
    old_value: Optional[Dict] = None
    new_value: Optional[Dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogRead(AuditLogBase):
    id: uuid.UUID
    created_at: datetime
