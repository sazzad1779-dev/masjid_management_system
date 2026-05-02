import uuid
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    email: str
    role: str = "viewer"
    masjid_id: Optional[uuid.UUID] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    masjid_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    masjid_id: Optional[str] = None
