import uuid
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import date, datetime, timedelta, UTC
from sqlmodel import Session, select, func, and_
from src.models.income import Income
from src.models.expense import Expense
from src.models.account import Account, AccountTransfer
from src.models.donation import DonationRecord
from src.models.donor import Donor
from src.schemas.reports import (
    SummaryStats, WeeklySummary, MonthlySummary, 
    YearlySummary, MonthlyComparison, DonorCollectionReport,
    AccountStatement
)

class ReportService:
    def get_dashboard_summary(self, session: Session, masjid_id: uuid.UUID) -> SummaryStats:
        # 1. Total Balance
        accounts = session.exec(select(Account).where(Account.masjid_id == masjid_id)).all()
        total_balance = Decimal(0)
        for account in accounts:
            opening = Decimal(str(account.opening_balance))
            
            income = session.exec(select(func.sum(Income.amount)).where(
                Income.account_id == account.id, Income.is_deleted == False
            )).one() or 0
            
            expense = session.exec(select(func.sum(Expense.amount)).where(
                Expense.account_id == account.id, Expense.is_deleted == False
            )).one() or 0
            
            tx_out = session.exec(select(func.sum(AccountTransfer.amount)).where(
                AccountTransfer.from_account_id == account.id
            )).one() or 0
            
            tx_in = session.exec(select(func.sum(AccountTransfer.amount)).where(
                AccountTransfer.to_account_id == account.id
            )).one() or 0
            
            total_balance += opening + Decimal(str(income)) - Decimal(str(expense)) - Decimal(str(tx_out)) + Decimal(str(tx_in))

        # 2. This Month Income & Expenses
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        
        this_month_income = session.exec(select(func.sum(Income.amount)).where(
            Income.masjid_id == masjid_id,
            Income.income_date >= start_of_month,
            Income.is_deleted == False
        )).one() or 0
        
        this_month_expense = session.exec(select(func.sum(Expense.amount)).where(
            Expense.masjid_id == masjid_id,
            Expense.expense_date >= start_of_month,
            Expense.is_deleted == False
        )).one() or 0

        # 3. Pending Donations
        current_month_str = today.strftime("%Y-%m")
        pending_donations = session.exec(select(func.count(DonationRecord.id)).where(
            DonationRecord.masjid_id == masjid_id,
            DonationRecord.month == current_month_str,
            DonationRecord.status == "pending"
        )).one() or 0

        # 4. Recent Transactions
        incomes = session.exec(select(Income).where(
            Income.masjid_id == masjid_id, Income.is_deleted == False
        ).order_by(Income.income_date.desc()).limit(5)).all()
        
        expenses = session.exec(select(Expense).where(
            Expense.masjid_id == masjid_id, Expense.is_deleted == False
        ).order_by(Expense.expense_date.desc()).limit(5)).all()
        
        recent = []
        for i in incomes:
            recent.append({"type": "income", "title": i.title, "amount": i.amount, "date": i.income_date})
        for e in expenses:
            recent.append({"type": "expense", "title": e.title, "amount": e.amount, "date": e.expense_date})
            
        recent.sort(key=lambda x: x["date"], reverse=True)
        recent = recent[:10]

        return SummaryStats(
            total_balance=total_balance,
            this_month_income=this_month_income,
            this_month_expenses=this_month_expense,
            pending_donations_count=pending_donations,
            recent_transactions=recent
        )

    def get_weekly_report(self, session: Session, masjid_id: uuid.UUID, start_date: date) -> WeeklySummary:
        end_date = start_date + timedelta(days=6)
        
        income = session.exec(select(func.sum(Income.amount)).where(
            Income.masjid_id == masjid_id,
            Income.income_date >= start_date,
            Income.income_date <= end_date,
            Income.is_deleted == False
        )).one() or 0
        
        expense = session.exec(select(func.sum(Expense.amount)).where(
            Expense.masjid_id == masjid_id,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date,
            Expense.is_deleted == False
        )).one() or 0
        
        return WeeklySummary(
            week_start=start_date,
            week_end=end_date,
            total_income=income,
            total_expense=expense,
            net_balance=Decimal(str(income)) - Decimal(str(expense))
        )

    def get_monthly_report(self, session: Session, masjid_id: uuid.UUID, year: int, month: int) -> MonthlySummary:
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
            
        income = session.exec(select(func.sum(Income.amount)).where(
            Income.masjid_id == masjid_id,
            Income.income_date >= start_date,
            Income.income_date <= end_date,
            Income.is_deleted == False
        )).one() or 0
        
        expense = session.exec(select(func.sum(Expense.amount)).where(
            Expense.masjid_id == masjid_id,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date,
            Expense.is_deleted == False
        )).one() or 0
        
        # Category breakdown
        income_cat = session.exec(select(Income.category, func.sum(Income.amount)).where(
            Income.masjid_id == masjid_id,
            Income.income_date >= start_date,
            Income.income_date <= end_date,
            Income.is_deleted == False
        ).group_by(Income.category)).all()
        
        expense_cat = session.exec(select(Expense.category, func.sum(Expense.amount)).where(
            Expense.masjid_id == masjid_id,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date,
            Expense.is_deleted == False
        ).group_by(Expense.category)).all()
        
        return MonthlySummary(
            month=f"{year}-{month:02d}",
            total_income=income,
            total_expense=expense,
            net_balance=Decimal(str(income)) - Decimal(str(expense)),
            category_breakdown_income={c: a for c, a in income_cat},
            category_breakdown_expense={c: a for c, a in expense_cat}
        )

    def get_yearly_report(self, session: Session, masjid_id: uuid.UUID, year: int) -> YearlySummary:
        monthly_data = []
        total_income = Decimal(0)
        total_expense = Decimal(0)
        
        for m in range(1, 13):
            start_date = date(year, m, 1)
            if m == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, m + 1, 1) - timedelta(days=1)
                
            inc = session.exec(select(func.sum(Income.amount)).where(
                Income.masjid_id == masjid_id,
                Income.income_date >= start_date,
                Income.income_date <= end_date,
                Income.is_deleted == False
            )).one() or 0
            
            exp = session.exec(select(func.sum(Expense.amount)).where(
                Expense.masjid_id == masjid_id,
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date,
                Expense.is_deleted == False
            )).one() or 0
            
            monthly_data.append(MonthlyComparison(
                month=f"{year}-{m:02d}",
                income=inc,
                expense=exp
            ))
            total_income += Decimal(str(inc))
            total_expense += Decimal(str(exp))
            
        return YearlySummary(
            year=year,
            total_income=total_income,
            total_expense=total_expense,
            net_balance=total_income - total_expense,
            monthly_data=monthly_data
        )

    def get_donor_collection_report(self, session: Session, masjid_id: uuid.UUID, month: str) -> DonorCollectionReport:
        records = session.exec(select(DonationRecord).where(
            DonationRecord.masjid_id == masjid_id,
            DonationRecord.month == month
        )).all()
        
        total_pledged = sum(r.pledged_amount for r in records)
        total_paid = sum(r.paid_amount or 0 for r in records)
        
        status_counts = {}
        for r in records:
            status_counts[r.status] = status_counts.get(r.status, 0) + 1
            
        donor_details = []
        for r in records:
            donor = session.get(Donor, r.donor_id)
            donor_details.append({
                "donor_name": donor.full_name if donor else "Unknown",
                "pledged": r.pledged_amount,
                "paid": r.paid_amount,
                "status": r.status,
                "payment_date": r.payment_date
            })
            
        return DonorCollectionReport(
            month=month,
            total_pledged=Decimal(str(total_pledged)),
            total_paid=Decimal(str(total_paid)),
            status_counts=status_counts,
            donor_details=donor_details
        )

report_service = ReportService()
