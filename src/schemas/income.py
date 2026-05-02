import uuid
from typing import Optional
from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel, Field

class IncomeBase(BaseModel):
    title: str
    amount: Decimal = Field(max_digits=15, decimal_places=2, gt=0)
    category: str
    income_date: date
    currency: str = "USD"
    source: Optional[str] = None
    payment_method: str = "Cash"
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    account_id: Optional[uuid.UUID] = None
    donor_id: Optional[uuid.UUID] = None

class IncomeCreate(IncomeBase):
    masjid_id: uuid.UUID
    recorded_by: uuid.UUID

class IncomeUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2, gt=0)
    category: Optional[str] = None
    income_date: Optional[date] = None
    currency: Optional[str] = None
    source: Optional[str] = None
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    account_id: Optional[uuid.UUID] = None
    donor_id: Optional[uuid.UUID] = None
    is_deleted: Optional[bool] = None

class IncomeBaseCreate(BaseModel):
    masjid_id: uuid.UUID
    title: str
    amount: Decimal = Field(max_digits=15, decimal_places=2, gt=0)
    category: str
    income_date: date
    currency: str = "USD"
    source: Optional[str] = None
    payment_method: str = "Cash"
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    account_id: Optional[uuid.UUID] = None
    donor_id: Optional[uuid.UUID] = None

class IncomeRead(IncomeBase):
    id: uuid.UUID
    masjid_id: uuid.UUID
    recorded_by: uuid.UUID
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
