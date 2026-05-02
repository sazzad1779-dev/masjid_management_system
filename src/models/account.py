import uuid
from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC

class Account(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    masjid_id: uuid.UUID = Field(foreign_key="masjid.id", index=True)
    account_name: str = Field(index=True)
    account_type: str  # Cash, Bank, Mobile Banking, Other
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    opening_balance: float = Field(default=0.0)
    opening_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = Field(default=True)
    notes: Optional[str] = None
    created_by: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class AccountTransfer(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    masjid_id: uuid.UUID = Field(foreign_key="masjid.id", index=True)
    from_account_id: uuid.UUID = Field(foreign_key="account.id")
    to_account_id: uuid.UUID = Field(foreign_key="account.id")
    amount: float
    currency: str
    transfer_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    notes: Optional[str] = None
    recorded_by: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
