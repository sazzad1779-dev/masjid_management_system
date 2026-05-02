import uuid
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class AccountBase(BaseModel):
    account_name: str
    account_type: str
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    opening_balance: float = 0.0
    opening_date: Optional[datetime] = None
    is_active: bool = True
    notes: Optional[str] = None

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    opening_balance: Optional[float] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class AccountRead(AccountBase):
    id: uuid.UUID
    masjid_id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AccountBalance(BaseModel):
    account_id: uuid.UUID
    account_name: str
    current_balance: float

class AccountTransferBase(BaseModel):
    from_account_id: uuid.UUID
    to_account_id: uuid.UUID
    amount: float
    currency: str = "USD"
    notes: Optional[str] = None

class AccountTransferCreate(AccountTransferBase):
    transfer_date: Optional[datetime] = None

class AccountTransferRead(AccountTransferBase):
    id: uuid.UUID
    masjid_id: uuid.UUID
    recorded_by: uuid.UUID
    transfer_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True
