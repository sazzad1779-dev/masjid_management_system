from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from src.db.session import get_session
from src.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseUpdate, ExpenseBaseCreate
from src.crud import crud_expense
from src.api.dependencies import get_current_user, RoleChecker
from src.models.user import User
import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional

router = APIRouter()

# Helper for roles
allow_write = RoleChecker(["super_admin", "admin", "committee", "cashier"])
allow_delete = RoleChecker(["super_admin", "admin"])

@router.post("/", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(
    *,
    session: Session = Depends(get_session),
    obj_in: ExpenseBaseCreate,
    current_user: User = Depends(allow_write)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)
    
    if current_role != "super_admin" and str(current_masjid_id) != str(obj_in.masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    expense_in = ExpenseCreate(
        **obj_in.model_dump(),
        recorded_by=current_user.id
    )
    return crud_expense.expense.create(session=session, obj_in=expense_in)

@router.get("/", response_model=List[ExpenseRead])
def read_expenses(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return crud_expense.expense.get_multi_by_masjid(
        session=session,
        masjid_id=masjid_id,
        skip=skip,
        limit=limit,
        category=category,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/summary", response_model=dict)
def get_monthly_summary(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    year: int,
    month: int,
    current_user: User = Depends(get_current_user)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return crud_expense.expense.get_monthly_summary(session=session, masjid_id=masjid_id, year=year, month=month)

@router.get("/{id}", response_model=ExpenseRead)
def read_expense(
    *,
    session: Session = Depends(get_session),
    id: uuid.UUID,
    current_user: User = Depends(get_current_user)
):
    db_obj = crud_expense.expense.get(session=session, id=id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Expense record not found")
    
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(db_obj.masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return db_obj

@router.patch("/{id}", response_model=ExpenseRead)
def update_expense(
    *,
    session: Session = Depends(get_session),
    id: uuid.UUID,
    obj_in: ExpenseUpdate,
    current_user: User = Depends(allow_write)
):
    db_obj = crud_expense.expense.get(session=session, id=id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Expense record not found")
    
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(db_obj.masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return crud_expense.expense.update(session=session, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", response_model=ExpenseRead)
def delete_expense(
    *,
    session: Session = Depends(get_session),
    id: uuid.UUID,
    current_user: User = Depends(allow_delete)
):
    db_obj = crud_expense.expense.get(session=session, id=id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Expense record not found")
    
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(db_obj.masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return crud_expense.expense.remove(session=session, id=id, deleted_by=current_user.id)
