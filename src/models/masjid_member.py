import uuid
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, UTC

if TYPE_CHECKING:
    from .user import User
    from .masjid import Masjid

class MasjidMember(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    masjid_id: uuid.UUID = Field(foreign_key="masjid.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    role: str = Field(default="viewer")  # super_admin, admin, committee, cashier, donor, viewer
    is_active: bool = Field(default=True)
    joined_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    user: "User" = Relationship(back_populates="memberships")
    # masjid: "Masjid" = Relationship(back_populates="members")
