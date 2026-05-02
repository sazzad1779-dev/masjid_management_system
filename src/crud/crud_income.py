from typing import List, Optional
from sqlmodel import Session, select, and_, func
from src.models.income import Income
from src.schemas.income import IncomeCreate, IncomeUpdate
import uuid
from datetime import date, datetime, timedelta, UTC

class CRUDIncome:
    def create(self, session: Session, obj_in: IncomeCreate) -> Income:
        db_obj = Income.model_validate(obj_in)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def get(self, session: Session, id: uuid.UUID) -> Optional[Income]:
        return session.get(Income, id)

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
    ) -> List[Income]:
        statement = select(Income).where(Income.masjid_id == masjid_id)
        
        if not include_deleted:
            statement = statement.where(Income.is_deleted == False)
        
        if category:
            statement = statement.where(Income.category == category)
        
        if start_date:
            statement = statement.where(Income.income_date >= start_date)
        
        if end_date:
            statement = statement.where(Income.income_date <= end_date)
            
        statement = statement.offset(skip).limit(limit).order_by(Income.income_date.desc())
        return session.exec(statement).all()

    def update(self, session: Session, db_obj: Income, obj_in: IncomeUpdate) -> Income:
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            setattr(db_obj, field, obj_data[field])
        
        db_obj.updated_at = datetime.now(UTC)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def remove(self, session: Session, id: uuid.UUID, deleted_by: uuid.UUID) -> Optional[Income]:
        db_obj = session.get(Income, id)
        if db_obj:
            db_obj.is_deleted = True
            db_obj.deleted_at = datetime.now(UTC)
            db_obj.deleted_by = deleted_by
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
        return db_obj

    def get_weekly_summary(self, session: Session, masjid_id: uuid.UUID, start_date: date) -> dict:
        end_date = start_date + timedelta(days=6)
        statement = select(func.sum(Income.amount)).where(
            and_(
                Income.masjid_id == masjid_id,
                Income.income_date >= start_date,
                Income.income_date <= end_date,
                Income.is_deleted == False
            )
        )
        total_income = session.exec(statement).one() or 0
        return {
            "masjid_id": masjid_id,
            "start_date": start_date,
            "end_date": end_date,
            "total_income": total_income
        }

income = CRUDIncome()
