import uuid
from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: str = "viewer"  # e.g. super_admin, admin, viewer, donor
    masjid_id: Optional[uuid.UUID] = Field(default=None, foreign_key="masjid.id")
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
