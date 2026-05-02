from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
import uuid
from typing import List, Optional
from src.db.session import get_session
from src.schemas.donation import DonationRecordRead, DonationGenerate, DonationVerify
from src.crud import crud_donation
from src.api.dependencies import get_current_user, RoleChecker
from src.models.user import User
from src.services.notification import NotificationService

router = APIRouter()

# Helper for roles
allow_write = RoleChecker(["super_admin", "admin", "committee"])
allow_cashier = RoleChecker(["super_admin", "admin", "committee", "cashier"])

@router.get("/", response_model=List[DonationRecordRead])
def read_donations(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    month: Optional[str] = None,
    donor_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(allow_cashier)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return crud_donation.get_donation_records(
        session, 
        masjid_id=masjid_id, 
        month=month, 
        donor_id=donor_id, 
        skip=skip, 
        limit=limit
    )

@router.post("/generate", response_model=List[DonationRecordRead])
def generate_donations(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    obj_in: DonationGenerate,
    current_user: User = Depends(allow_write)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return crud_donation.generate_monthly_donations(session, masjid_id=masjid_id, month=obj_in.month)

@router.put("/{record_id}/verify", response_model=DonationRecordRead)
def verify_donation(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    record_id: uuid.UUID,
    obj_in: DonationVerify,
    current_user: User = Depends(allow_write)
):
    record = crud_donation.get_donation_record(session, record_id)
    if not record or record.masjid_id != masjid_id:
        raise HTTPException(status_code=404, detail="Donation record not found")
    
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    donation = crud_donation.verify_donation_payment(
        session, 
        db_obj=record, 
        obj_in=obj_in, 
        user_id=current_user.id
    )

    # Notify donor if they have a user account
    if donation.donor.user_id:
        NotificationService.create_notification(
            db=session,
            masjid_id=donation.masjid_id,
            user_id=donation.donor.user_id,
            type="donation_verified",
            title="Donation Verified",
            body=f"Your donation for {donation.month} has been verified as paid: {donation.paid_amount} {donation.donor.pledge_currency}",
            related_entity_type="donation",
            related_entity_id=donation.id
        )
    
    return donation
