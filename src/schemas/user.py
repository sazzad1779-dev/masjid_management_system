import uuid
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class MasjidMemberBase(BaseModel):
    masjid_id: uuid.UUID
    role: str = "viewer"
    is_active: bool = True

class MasjidMemberCreate(MasjidMemberBase):
    user_id: uuid.UUID

class MasjidMemberRead(MasjidMemberBase):
    id: uuid.UUID
    user_id: uuid.UUID
    joined_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserSignup(UserCreate):
    institution_name: str
    admin_name: str

class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    memberships: List[MasjidMemberRead] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    masjid_id: Optional[str] = None
    type: Optional[str] = None

class UserInvite(BaseModel):
    email: str
    role: str = "viewer"
    masjid_id: uuid.UUID
