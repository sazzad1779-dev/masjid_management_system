import uuid
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date

class DonationRecordBase(BaseModel):
    month: str  # YYYY-MM
    pledged_amount: float
    paid_amount: Optional[float] = 0.0
    payment_date: Optional[date] = None
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    status: str = "pending"
    verification_note: Optional[str] = None

class DonationRecordCreate(DonationRecordBase):
    donor_id: uuid.UUID

class DonationRecordUpdate(BaseModel):
    paid_amount: Optional[float] = None
    payment_date: Optional[date] = None
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    status: Optional[str] = None
    verification_note: Optional[str] = None
    receipt_url: Optional[str] = None

class DonationRecordRead(DonationRecordBase):
    id: uuid.UUID
    masjid_id: uuid.UUID
    donor_id: uuid.UUID
    verified_by: Optional[uuid.UUID] = None
    receipt_url: Optional[str] = None
    income_record_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DonationGenerate(BaseModel):
    month: str  # YYYY-MM

class DonationVerify(BaseModel):
    paid_amount: float
    payment_date: date
    payment_method: str
    account_id: uuid.UUID
    reference_number: Optional[str] = None
    verification_note: Optional[str] = None
