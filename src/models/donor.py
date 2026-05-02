import uuid
from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC, date

class Donor(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    masjid_id: uuid.UUID = Field(foreign_key="masjid.id", index=True)
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id", index=True)
    full_name: str = Field(index=True)
    phone: str = Field(index=True)
    email: Optional[str] = Field(default=None, index=True)
    address: Optional[str] = None
    monthly_pledge_amount: float
    pledge_currency: str
    pledge_start_date: date
    pledge_end_date: Optional[date] = None
    payment_method: str  # Cash, Bank Transfer, Mobile Banking, Other
    notes: Optional[str] = None
    is_active: bool = Field(default=True)
    created_by: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
