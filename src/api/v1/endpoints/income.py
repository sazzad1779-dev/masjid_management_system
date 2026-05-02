from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from src.db.session import get_session
from src.schemas.income import IncomeCreate, IncomeRead, IncomeUpdate, IncomeBaseCreate
from src.crud import crud_income
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

@router.post("/", response_model=IncomeRead, status_code=status.HTTP_201_CREATED)
def create_income(
    *,
    session: Session = Depends(get_session),
    obj_in: IncomeBaseCreate, # I'll use a slightly different schema for the request
    current_user: User = Depends(allow_write)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)
    
    if current_role != "super_admin" and str(current_masjid_id) != str(obj_in.masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    income_in = IncomeCreate(
        **obj_in.model_dump(),
        recorded_by=current_user.id
    )
    return crud_income.income.create(session=session, obj_in=income_in)

@router.get("/", response_model=List[IncomeRead])
def read_incomes(
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
    
    return crud_income.income.get_multi_by_masjid(
        session=session,
        masjid_id=masjid_id,
        skip=skip,
        limit=limit,
        category=category,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/weekly", response_model=dict)
def get_weekly_summary(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    start_date: date,
    current_user: User = Depends(get_current_user)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return crud_income.income.get_weekly_summary(session=session, masjid_id=masjid_id, start_date=start_date)

@router.get("/{id}", response_model=IncomeRead)
def read_income(
    *,
    session: Session = Depends(get_session),
    id: uuid.UUID,
    current_user: User = Depends(get_current_user)
):
    db_obj = crud_income.income.get(session=session, id=id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Income record not found")
    
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(db_obj.masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return db_obj

@router.patch("/{id}", response_model=IncomeRead)
def update_income(
    *,
    session: Session = Depends(get_session),
    id: uuid.UUID,
    obj_in: IncomeUpdate,
    current_user: User = Depends(allow_write)
):
    db_obj = crud_income.income.get(session=session, id=id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Income record not found")
    
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(db_obj.masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return crud_income.income.update(session=session, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", response_model=IncomeRead)
def delete_income(
    *,
    session: Session = Depends(get_session),
    id: uuid.UUID,
    current_user: User = Depends(allow_delete)
):
    db_obj = crud_income.income.get(session=session, id=id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Income record not found")
    
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(db_obj.masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return crud_income.income.remove(session=session, id=id, deleted_by=current_user.id)

