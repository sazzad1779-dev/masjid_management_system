import uuid
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, date

class DonorBase(BaseModel):
    full_name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    monthly_pledge_amount: float
    pledge_currency: str = "USD"
    pledge_start_date: date
    pledge_end_date: Optional[date] = None
    payment_method: str = "Cash"
    notes: Optional[str] = None
    is_active: bool = True

class DonorCreate(DonorBase):
    pass

class DonorUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    monthly_pledge_amount: Optional[float] = None
    pledge_currency: Optional[str] = None
    pledge_start_date: Optional[date] = None
    pledge_end_date: Optional[date] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class DonorRead(DonorBase):
    id: uuid.UUID
    masjid_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
