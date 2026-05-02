import uuid
from typing import Optional
from decimal import Decimal
from datetime import datetime, date, UTC
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Numeric

class Income(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    masjid_id: uuid.UUID = Field(foreign_key="masjid.id", index=True)
    account_id: Optional[uuid.UUID] = Field(default=None, index=True) # Will be linked to accounts later
    
    title: str = Field(index=True)
    amount: Decimal = Field(sa_column=Column(Numeric(precision=15, scale=2)))
    currency: str = Field(default="USD")
    income_date: date = Field(default_factory=date.today, index=True)
    category: str = Field(index=True) # e.g. "Friday Jumu'ah Collection", "Zakat", etc.
    source: Optional[str] = None
    payment_method: str = Field(default="Cash") # Cash, Bank Transfer, etc.
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    donor_id: Optional[uuid.UUID] = Field(default=None, index=True) # Optional link to a donor
    
    recorded_by: uuid.UUID = Field(foreign_key="user.id")
    
    # Soft Delete
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[uuid.UUID] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
