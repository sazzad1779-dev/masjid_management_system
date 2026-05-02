import uuid
from typing import Optional
from decimal import Decimal
from datetime import datetime, date, UTC
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Numeric

class Expense(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    masjid_id: uuid.UUID = Field(foreign_key="masjid.id", index=True)
    account_id: Optional[uuid.UUID] = Field(default=None, index=True)
    
    title: str = Field(index=True)
    amount: Decimal = Field(sa_column=Column(Numeric(precision=15, scale=2)))
    currency: str = Field(default="USD")
    expense_date: date = Field(default_factory=date.today, index=True)
    category: str = Field(index=True) # e.g. "Utility Bills", "Salary", etc.
    vendor: Optional[str] = None
    payment_method: str = Field(default="Cash")
    reference_number: Optional[str] = None
    
    is_recurring: bool = Field(default=False)
    recurring_template_id: Optional[uuid.UUID] = Field(default=None, index=True)
    
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    approved_by: Optional[uuid.UUID] = None
    recorded_by: uuid.UUID = Field(foreign_key="user.id")
    
    # Soft Delete
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[uuid.UUID] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class RecurringExpenseTemplate(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    masjid_id: uuid.UUID = Field(foreign_key="masjid.id", index=True)
    
    title: str = Field(index=True)
    estimated_amount: Decimal = Field(sa_column=Column(Numeric(precision=15, scale=2)))
    category: str = Field(index=True)
    vendor: Optional[str] = None
    payment_method: str = Field(default="Cash")
    
    frequency: str = Field(default="monthly") # monthly, weekly, yearly
    due_day_of_month: Optional[int] = Field(default=1)
    
    is_active: bool = Field(default=True)
    notes: Optional[str] = None
    
    created_by: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
