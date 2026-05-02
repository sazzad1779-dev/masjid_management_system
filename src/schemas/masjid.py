import uuid
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Shared properties
class MasjidBase(BaseModel):
    name: str
    slug: str
    address: str
    city: str
    country: str
    contact_email: str
    phone: Optional[str] = None
    logo_url: Optional[str] = None
    currency: str = "USD"
    fiscal_year_start: str = "January"
    primary_color: str = "#000000"
    secondary_color: str = "#ffffff"
    social_media: dict = {}
    is_public: bool = True
    is_active: bool = True

# Properties to receive via API on creation
class MasjidCreate(MasjidBase):
    pass

# Properties to receive via API on update
class MasjidUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    logo_url: Optional[str] = None
    currency: Optional[str] = None
    fiscal_year_start: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    social_media: Optional[dict] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None

# Properties to return via API
class MasjidRead(MasjidBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
