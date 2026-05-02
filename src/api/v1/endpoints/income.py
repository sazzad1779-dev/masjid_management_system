from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlmodel import Session
from src.db.session import get_session
from src.schemas.income import IncomeCreate, IncomeRead, IncomeUpdate, IncomeBaseCreate
from src.crud import crud_income
from src.api.dependencies import get_current_user, RoleChecker
from src.models.user import User
from src.services.notification import NotificationService
from src.services.audit_log import AuditLogService
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
    request: Request,
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
    income = crud_income.income.create(session=session, obj_in=income_in)
    
    # Notify admins
    NotificationService.notify_masjid_admins(
        db=session,
        masjid_id=income.masjid_id,
        type="income_recorded",
        title="New Income Recorded",
        body=f"New income of {income.amount} {income.currency} recorded: {income.title}",
        related_entity_type="income",
        related_entity_id=income.id
    )
    
    # Audit Log
    AuditLogService.log_action(
        db=session,
        user_id=current_user.id,
        user_name=current_user.email,
        action="create",
        entity_type="income",
        masjid_id=income.masjid_id,
        entity_id=income.id,
        new_value=income.model_dump(),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return income

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
    request: Request,
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
    
    old_value = db_obj.model_dump()
    updated_obj = crud_income.income.update(session=session, db_obj=db_obj, obj_in=obj_in)
    
    # Audit Log
    AuditLogService.log_action(
        db=session,
        user_id=current_user.id,
        user_name=current_user.email,
        action="update",
        entity_type="income",
        masjid_id=updated_obj.masjid_id,
        entity_id=updated_obj.id,
        old_value=old_value,
        new_value=updated_obj.model_dump(),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return updated_obj

@router.delete("/{id}", response_model=IncomeRead)
def delete_income(
    *,
    session: Session = Depends(get_session),
    request: Request,
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
    
    old_value = db_obj.model_dump()
    removed_obj = crud_income.income.remove(session=session, id=id, deleted_by=current_user.id)
    
    # Audit Log
    AuditLogService.log_action(
        db=session,
        user_id=current_user.id,
        user_name=current_user.email,
        action="delete",
        entity_type="income",
        masjid_id=removed_obj.masjid_id,
        entity_id=removed_obj.id,
        old_value=old_value,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return removed_obj

