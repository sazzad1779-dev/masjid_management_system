import uuid
from typing import Optional, Dict
from sqlmodel import Field, SQLModel, JSON, Column
from datetime import datetime, UTC

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    masjid_id: Optional[uuid.UUID] = Field(default=None, index=True)
    user_id: uuid.UUID = Field(index=True)
    user_name: str
    action: str = Field(index=True) # create, update, delete, login, logout, etc.
    entity_type: str = Field(index=True) # income, expense, account, etc.
    entity_id: Optional[uuid.UUID] = Field(default=None, index=True)
    old_value: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    new_value: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
