from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlmodel import Session
from src.db.session import get_session
from src.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseUpdate, ExpenseBaseCreate
from src.crud import crud_expense
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

@router.post("/", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(
    *,
    session: Session = Depends(get_session),
    request: Request,
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
    expense = crud_expense.expense.create(session=session, obj_in=expense_in)
    
    # Notify admins
    NotificationService.notify_masjid_admins(
        db=session,
        masjid_id=expense.masjid_id,
        type="expense_recorded",
        title="New Expense Recorded",
        body=f"New expense of {expense.amount} {expense.currency} recorded: {expense.title}",
        related_entity_type="expense",
        related_entity_id=expense.id
    )
    
    # Audit Log
    AuditLogService.log_action(
        db=session,
        user_id=current_user.id,
        user_name=current_user.email,
        action="create",
        entity_type="expense",
        masjid_id=expense.masjid_id,
        entity_id=expense.id,
        new_value=expense.model_dump(),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return expense

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
    request: Request,
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
    
    old_value = db_obj.model_dump()
    updated_obj = crud_expense.expense.update(session=session, db_obj=db_obj, obj_in=obj_in)
    
    # Audit Log
    AuditLogService.log_action(
        db=session,
        user_id=current_user.id,
        user_name=current_user.email,
        action="update",
        entity_type="expense",
        masjid_id=updated_obj.masjid_id,
        entity_id=updated_obj.id,
        old_value=old_value,
        new_value=updated_obj.model_dump(),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return updated_obj

@router.delete("/{id}", response_model=ExpenseRead)
def delete_expense(
    *,
    session: Session = Depends(get_session),
    request: Request,
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
    
    old_value = db_obj.model_dump()
    removed_obj = crud_expense.expense.remove(session=session, id=id, deleted_by=current_user.id)
    
    # Audit Log
    AuditLogService.log_action(
        db=session,
        user_id=current_user.id,
        user_name=current_user.email,
        action="delete",
        entity_type="expense",
        masjid_id=removed_obj.masjid_id,
        entity_id=removed_obj.id,
        old_value=old_value,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return removed_obj
