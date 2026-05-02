import uuid
from typing import Optional, Dict
from sqlmodel import Field, SQLModel, JSON, Column
from datetime import datetime, UTC

# SQLAlchemy / SQLModel ORM definition
class Masjid(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    slug: str = Field(unique=True, index=True)
    address: str
    city: str
    country: str
    contact_email: str
    phone: Optional[str] = None
    logo_url: Optional[str] = None
    currency: str = Field(default="USD")
    fiscal_year_start: str = Field(default="January")
    primary_color: str = Field(default="#000000")
    secondary_color: str = Field(default="#ffffff")
    social_media: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    is_public: bool = True
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
