from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlmodel import Session
import uuid
from typing import List, Optional
from src.db.session import get_session
from src.schemas.donor import DonorCreate, DonorRead, DonorUpdate
from src.crud import crud_donor
from src.api.dependencies import get_current_user, RoleChecker
from src.models.user import User
from src.services.audit_log import AuditLogService

router = APIRouter()

# Helper for roles
allow_write = RoleChecker(["super_admin", "admin", "committee"])
allow_read = RoleChecker(["super_admin", "admin", "committee", "cashier"])

@router.get("/me", response_model=DonorRead)
def read_donor_me(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get current donor profile based on token.
    """
    donor = crud_donor.get_donor_by_user_id(session, user_id=current_user.id)
    if not donor:
        raise HTTPException(status_code=404, detail="Donor profile not found for this user")
    return donor

@router.post("/", response_model=DonorRead, status_code=status.HTTP_201_CREATED)
def create_donor(
    *,
    session: Session = Depends(get_session),
    request: Request,
    masjid_id: uuid.UUID,
    obj_in: DonorCreate,
    current_user: User = Depends(allow_write)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    donor = crud_donor.create_donor(session, obj_in=obj_in, masjid_id=masjid_id, user_id=current_user.id)
    
    # Audit Log
    AuditLogService.log_action(
        db=session,
        user_id=current_user.id,
        user_name=current_user.email,
        action="create",
        entity_type="donor",
        masjid_id=masjid_id,
        entity_id=donor.id,
        new_value=donor.model_dump(),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return donor

@router.get("/", response_model=List[DonorRead])
def read_donors(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(allow_read)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return crud_donor.get_donors(session, masjid_id=masjid_id, skip=skip, limit=limit)

@router.get("/{donor_id}", response_model=DonorRead)
def read_donor(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    donor_id: uuid.UUID,
    current_user: User = Depends(allow_read)
):
    donor = crud_donor.get_donor(session, donor_id)
    if not donor or donor.masjid_id != masjid_id:
        raise HTTPException(status_code=404, detail="Donor not found")
    
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return donor

@router.put("/{donor_id}", response_model=DonorRead)
def update_donor(
    *,
    session: Session = Depends(get_session),
    request: Request,
    masjid_id: uuid.UUID,
    donor_id: uuid.UUID,
    obj_in: DonorUpdate,
    current_user: User = Depends(allow_write)
):
    donor = crud_donor.get_donor(session, donor_id)
    if not donor or donor.masjid_id != masjid_id:
        raise HTTPException(status_code=404, detail="Donor not found")
    
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    old_value = donor.model_dump()
    updated_donor = crud_donor.update_donor(session, db_obj=donor, obj_in=obj_in)
    
    # Audit Log
    AuditLogService.log_action(
        db=session,
        user_id=current_user.id,
        user_name=current_user.email,
        action="update",
        entity_type="donor",
        masjid_id=masjid_id,
        entity_id=updated_donor.id,
        old_value=old_value,
        new_value=updated_donor.model_dump(),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return updated_donor

@router.delete("/{donor_id}", response_model=DonorRead)
def delete_donor(
    *,
    session: Session = Depends(get_session),
    request: Request,
    masjid_id: uuid.UUID,
    donor_id: uuid.UUID,
    current_user: User = Depends(allow_write)
):
    donor = crud_donor.get_donor(session, donor_id)
    if not donor or donor.masjid_id != masjid_id:
        raise HTTPException(status_code=404, detail="Donor not found")
    
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    old_value = donor.model_dump()
    removed_donor = crud_donor.deactivate_donor(session, donor_id=donor_id)
    
    # Audit Log
    AuditLogService.log_action(
        db=session,
        user_id=current_user.id,
        user_name=current_user.email,
        action="deactivate",
        entity_type="donor",
        masjid_id=masjid_id,
        entity_id=removed_donor.id,
        old_value=old_value,
        new_value=removed_donor.model_dump(),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return removed_donor

@router.post("/{donor_id}/activate", response_model=DonorRead)
def activate_donor(
    *,
    session: Session = Depends(get_session),
    request: Request,
    masjid_id: uuid.UUID,
    donor_id: uuid.UUID,
    current_user: User = Depends(allow_write)
):
    donor = crud_donor.get_donor(session, donor_id)
    if not donor or donor.masjid_id != masjid_id:
        raise HTTPException(status_code=404, detail="Donor not found")

    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)
    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    old_value = donor.model_dump()
    activated = crud_donor.activate_donor(session, donor_id=donor_id)

    AuditLogService.log_action(
        db=session,
        user_id=current_user.id,
        user_name=current_user.email,
        action="activate",
        entity_type="donor",
        masjid_id=masjid_id,
        entity_id=activated.id,
        old_value=old_value,
        new_value=activated.model_dump(),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    return activated

@router.delete("/{donor_id}/hard", response_model=DonorRead)
def hard_delete_donor(
    *,
    session: Session = Depends(get_session),
    request: Request,
    masjid_id: uuid.UUID,
    donor_id: uuid.UUID,
    current_user: User = Depends(allow_write)
):
    """Permanently delete a donor record (use with caution)."""
    donor = crud_donor.get_donor(session, donor_id)
    if not donor or donor.masjid_id != masjid_id:
        raise HTTPException(status_code=404, detail="Donor not found")

    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)
    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    old_value = donor.model_dump()
    AuditLogService.log_action(
        db=session,
        user_id=current_user.id,
        user_name=current_user.email,
        action="hard_delete",
        entity_type="donor",
        masjid_id=masjid_id,
        entity_id=donor_id,
        old_value=old_value,
        new_value=None,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    crud_donor.hard_delete_donor(session, donor_id=donor_id)
    return donor
