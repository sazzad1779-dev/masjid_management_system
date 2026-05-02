from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session
from src.db.session import get_session
from src.schemas.audit_log import AuditLogRead
from src.crud.audit_log import audit_log
from src.api.dependencies import get_current_user, RoleChecker
from src.models.user import User
import uuid
from typing import List

router = APIRouter()

# Roles
allow_admin = RoleChecker(["super_admin", "admin"])
allow_super_admin = RoleChecker(["super_admin"])

@router.get("/masjids/{masjid_id}", response_model=List[AuditLogRead])
def read_audit_logs(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(allow_admin)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return audit_log.get_multi_by_masjid(session=session, masjid_id=masjid_id, skip=skip, limit=limit)

@router.get("/all", response_model=List[AuditLogRead])
def read_all_audit_logs(
    *,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(allow_super_admin)
):
    return audit_log.get_all(session=session, skip=skip, limit=limit)
