import uuid
from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC, date

class DonationRecord(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    masjid_id: uuid.UUID = Field(foreign_key="masjid.id", index=True)
    donor_id: uuid.UUID = Field(foreign_key="donor.id", index=True)
    month: str = Field(index=True)  # CHAR 7 — 'YYYY-MM'
    pledged_amount: float
    paid_amount: Optional[float] = Field(default=0.0)
    payment_date: Optional[date] = None
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    status: str = Field(default="pending")  # pending, paid, partial, missed
    verified_by: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    verification_note: Optional[str] = None
    receipt_url: Optional[str] = None
    income_record_id: Optional[uuid.UUID] = Field(default=None, foreign_key="income.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
