import uuid
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, UTC

class Notification(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    masjid_id: uuid.UUID = Field(foreign_key="masjid.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    type: str = Field(nullable=False)  # e.g., "income_recorded", "expense_recorded", "donation_verified"
    title: str = Field(nullable=False)
    body: str = Field(nullable=False)
    is_read: bool = Field(default=False)
    related_entity_type: Optional[str] = Field(default=None, nullable=True)
    related_entity_id: Optional[uuid.UUID] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
