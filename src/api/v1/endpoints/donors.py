from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
import uuid
from typing import List, Optional
from src.db.session import get_session
from src.schemas.donor import DonorCreate, DonorRead, DonorUpdate
from src.crud import crud_donor
from src.api.dependencies import get_current_user, RoleChecker
from src.models.user import User

router = APIRouter()

# Helper for roles
allow_write = RoleChecker(["super_admin", "admin", "committee"])
allow_read = RoleChecker(["super_admin", "admin", "committee", "cashier"])

@router.post("/", response_model=DonorRead, status_code=status.HTTP_201_CREATED)
def create_donor(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    obj_in: DonorCreate,
    current_user: User = Depends(allow_write)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return crud_donor.create_donor(session, obj_in=obj_in, masjid_id=masjid_id, user_id=current_user.id)

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
    
    return crud_donor.update_donor(session, db_obj=donor, obj_in=obj_in)

@router.delete("/{donor_id}", response_model=DonorRead)
def delete_donor(
    *,
    session: Session = Depends(get_session),
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
    
    return crud_donor.deactivate_donor(session, donor_id=donor_id)
