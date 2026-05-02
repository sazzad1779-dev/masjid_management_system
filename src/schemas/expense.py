import uuid
from typing import Optional
from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel, Field

class ExpenseBase(BaseModel):
    title: str
    amount: Decimal = Field(max_digits=15, decimal_places=2, gt=0)
    category: str
    expense_date: date
    currency: str = "USD"
    vendor: Optional[str] = None
    payment_method: str = "Cash"
    reference_number: Optional[str] = None
    is_recurring: bool = False
    recurring_template_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    account_id: Optional[uuid.UUID] = None
    approved_by: Optional[uuid.UUID] = None

class ExpenseCreate(ExpenseBase):
    masjid_id: uuid.UUID
    recorded_by: uuid.UUID

class ExpenseBaseCreate(BaseModel):
    masjid_id: uuid.UUID
    title: str
    amount: Decimal = Field(max_digits=15, decimal_places=2, gt=0)
    category: str
    expense_date: date
    currency: str = "USD"
    vendor: Optional[str] = None
    payment_method: str = "Cash"
    reference_number: Optional[str] = None
    is_recurring: bool = False
    recurring_template_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    account_id: Optional[uuid.UUID] = None
    approved_by: Optional[uuid.UUID] = None

class ExpenseUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2, gt=0)
    category: Optional[str] = None
    expense_date: Optional[date] = None
    currency: Optional[str] = None
    vendor: Optional[str] = None
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurring_template_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    account_id: Optional[uuid.UUID] = None
    approved_by: Optional[uuid.UUID] = None
    is_deleted: Optional[bool] = None

class ExpenseRead(ExpenseBase):
    id: uuid.UUID
    masjid_id: uuid.UUID
    recorded_by: uuid.UUID
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RecurringExpenseTemplateBase(BaseModel):
    title: str
    estimated_amount: Decimal = Field(max_digits=15, decimal_places=2, gt=0)
    category: str
    vendor: Optional[str] = None
    payment_method: str = "Cash"
    frequency: str = "monthly"
    due_day_of_month: Optional[int] = 1
    notes: Optional[str] = None
    is_active: bool = True

class RecurringExpenseTemplateCreate(RecurringExpenseTemplateBase):
    masjid_id: uuid.UUID
    created_by: uuid.UUID

class RecurringExpenseTemplateUpdate(BaseModel):
    title: Optional[str] = None
    estimated_amount: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2, gt=0)
    category: Optional[str] = None
    vendor: Optional[str] = None
    payment_method: Optional[str] = None
    frequency: Optional[str] = None
    due_day_of_month: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class RecurringExpenseTemplateRead(RecurringExpenseTemplateBase):
    id: uuid.UUID
    masjid_id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
