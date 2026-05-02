from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date
from pydantic import BaseModel

class SummaryStats(BaseModel):
    total_balance: Decimal
    this_month_income: Decimal
    this_month_expenses: Decimal
    pending_donations_count: int
    recent_transactions: List[Dict[str, Any]]

class WeeklySummary(BaseModel):
    week_start: date
    week_end: date
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal

class MonthlySummary(BaseModel):
    month: str  # YYYY-MM
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal
    category_breakdown_income: Dict[str, Decimal]
    category_breakdown_expense: Dict[str, Decimal]

class MonthlyComparison(BaseModel):
    month: str
    income: Decimal
    expense: Decimal

class YearlySummary(BaseModel):
    year: int
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal
    monthly_data: List[MonthlyComparison]

class CategorySummary(BaseModel):
    category: str
    amount: Decimal
    percentage: Decimal

class DonorCollectionReport(BaseModel):
    month: str
    total_pledged: Decimal
    total_paid: Decimal
    status_counts: Dict[str, int]
    donor_details: List[Dict[str, Any]]

class AccountStatement(BaseModel):
    account_name: str
    start_date: date
    end_date: date
    opening_balance: Decimal
    closing_balance: Decimal
    transactions: List[Dict[str, Any]]
