from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session
from src.db.session import get_session
from src.schemas.account import (
    AccountCreate, AccountRead, AccountUpdate, AccountBalance,
    AccountTransferCreate, AccountTransferRead
)
from src.crud import crud_account
from src.api.dependencies import get_current_user, RoleChecker
from src.models.user import User
from src.services.audit_log import AuditLogService
import uuid
from typing import List

router = APIRouter()

# Helper for roles
allow_write = RoleChecker(["super_admin", "admin", "committee", "cashier"])

@router.post("/", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def create_account(
    *,
    session: Session = Depends(get_session),
    request: Request,
    masjid_id: uuid.UUID,
    obj_in: AccountCreate,
    current_user: User = Depends(allow_write)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    account = crud_account.create_account(session, obj_in=obj_in, masjid_id=masjid_id, user_id=current_user.id)
    
    # Audit Log
    AuditLogService.log_action(
        db=session,
        user_id=current_user.id,
        user_name=current_user.email,
        action="create",
        entity_type="account",
        masjid_id=masjid_id,
        entity_id=account.id,
        new_value=account.model_dump(),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return account

@router.get("/", response_model=List[AccountRead])
def read_accounts(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return crud_account.get_accounts(session, masjid_id=masjid_id, skip=skip, limit=limit)

@router.get("/{account_id}/balance", response_model=AccountBalance)
def get_account_balance(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    account = crud_account.get_account(session, account_id)
    if not account or account.masjid_id != masjid_id:
        raise HTTPException(status_code=404, detail="Account not found")
    
    balance = crud_account.get_account_balance(session, account_id=account_id, masjid_id=masjid_id)
    return AccountBalance(
        account_id=account_id,
        account_name=account.account_name,
        current_balance=balance
    )

@router.post("/transfer", response_model=AccountTransferRead, status_code=status.HTTP_201_CREATED)
def create_transfer(
    *,
    session: Session = Depends(get_session),
    request: Request,
    masjid_id: uuid.UUID,
    obj_in: AccountTransferCreate,
    current_user: User = Depends(allow_write)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Verify accounts belong to the masjid
    from_acc = crud_account.get_account(session, obj_in.from_account_id)
    to_acc = crud_account.get_account(session, obj_in.to_account_id)
    
    if not from_acc or from_acc.masjid_id != masjid_id:
        raise HTTPException(status_code=404, detail="Source account not found")
    if not to_acc or to_acc.masjid_id != masjid_id:
        raise HTTPException(status_code=404, detail="Destination account not found")
        
    transfer = crud_account.create_transfer(session, obj_in=obj_in, masjid_id=masjid_id, user_id=current_user.id)
    
    # Audit Log
    AuditLogService.log_action(
        db=session,
        user_id=current_user.id,
        user_name=current_user.email,
        action="transfer",
        entity_type="account_transfer",
        masjid_id=masjid_id,
        entity_id=transfer.id,
        new_value=transfer.model_dump(),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return transfer

@router.get("/transfer", response_model=List[AccountTransferRead])
def read_transfers(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return crud_account.get_transfers(session, masjid_id=masjid_id, skip=skip, limit=limit)
