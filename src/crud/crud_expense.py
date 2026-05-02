from typing import List, Optional
from sqlmodel import Session, select, and_, func
from src.models.expense import Expense, RecurringExpenseTemplate
from src.schemas.expense import ExpenseCreate, ExpenseUpdate, RecurringExpenseTemplateCreate, RecurringExpenseTemplateUpdate
import uuid
from datetime import date, datetime, timedelta, UTC

class CRUDExpense:
    def create(self, session: Session, obj_in: ExpenseCreate) -> Expense:
        db_obj = Expense.model_validate(obj_in)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def get(self, session: Session, id: uuid.UUID) -> Optional[Expense]:
        return session.get(Expense, id)

    def get_multi_by_masjid(
        self, 
        session: Session, 
        masjid_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        include_deleted: bool = False
    ) -> List[Expense]:
        statement = select(Expense).where(Expense.masjid_id == masjid_id)
        
        if not include_deleted:
            statement = statement.where(Expense.is_deleted == False)
        
        if category:
            statement = statement.where(Expense.category == category)
        
        if start_date:
            statement = statement.where(Expense.expense_date >= start_date)
        
        if end_date:
            statement = statement.where(Expense.expense_date <= end_date)
            
        statement = statement.offset(skip).limit(limit).order_by(Expense.expense_date.desc())
        return session.exec(statement).all()

    def update(self, session: Session, db_obj: Expense, obj_in: ExpenseUpdate) -> Expense:
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            setattr(db_obj, field, obj_data[field])
        
        db_obj.updated_at = datetime.now(UTC)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def remove(self, session: Session, id: uuid.UUID, deleted_by: uuid.UUID) -> Optional[Expense]:
        db_obj = session.get(Expense, id)
        if db_obj:
            db_obj.is_deleted = True
            db_obj.deleted_at = datetime.now(UTC)
            db_obj.deleted_by = deleted_by
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
        return db_obj

    def get_monthly_summary(self, session: Session, masjid_id: uuid.UUID, year: int, month: int) -> dict:
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
            
        statement = select(func.sum(Expense.amount)).where(
            and_(
                Expense.masjid_id == masjid_id,
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date,
                Expense.is_deleted == False
            )
        )
        total_expense = session.exec(statement).one() or 0
        return {
            "masjid_id": masjid_id,
            "year": year,
            "month": month,
            "total_expense": total_expense
        }

class CRUDRecurringTemplate:
    def create(self, session: Session, obj_in: RecurringExpenseTemplateCreate) -> RecurringExpenseTemplate:
        db_obj = RecurringExpenseTemplate.model_validate(obj_in)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def get(self, session: Session, id: uuid.UUID) -> Optional[RecurringExpenseTemplate]:
        return session.get(RecurringExpenseTemplate, id)

    def get_multi_by_masjid(
        self, session: Session, masjid_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[RecurringExpenseTemplate]:
        statement = select(RecurringExpenseTemplate).where(RecurringExpenseTemplate.masjid_id == masjid_id)
        statement = statement.offset(skip).limit(limit)
        return session.exec(statement).all()

    def update(
        self, session: Session, db_obj: RecurringExpenseTemplate, obj_in: RecurringExpenseTemplateUpdate
    ) -> RecurringExpenseTemplate:
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            setattr(db_obj, field, obj_data[field])
        db_obj.updated_at = datetime.now(UTC)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

expense = CRUDExpense()
recurring_template = CRUDRecurringTemplate()
