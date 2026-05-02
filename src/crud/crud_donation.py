import uuid
from typing import List, Optional
from sqlmodel import Session, select, and_
from datetime import datetime, UTC
from src.models.donation import DonationRecord
from src.models.donor import Donor
from src.models.income import Income
from src.schemas.donation import DonationRecordCreate, DonationRecordUpdate, DonationVerify

def create_donation_record(db: Session, *, obj_in: DonationRecordCreate, masjid_id: uuid.UUID) -> DonationRecord:
    db_obj = DonationRecord(
        **obj_in.model_dump(),
        masjid_id=masjid_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_donation_record(db: Session, record_id: uuid.UUID) -> Optional[DonationRecord]:
    return db.get(DonationRecord, record_id)

def get_donation_records(
    db: Session, 
    *, 
    masjid_id: uuid.UUID, 
    month: Optional[str] = None, 
    donor_id: Optional[uuid.UUID] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[DonationRecord]:
    statement = select(DonationRecord).where(DonationRecord.masjid_id == masjid_id)
    if month:
        statement = statement.where(DonationRecord.month == month)
    if donor_id:
        statement = statement.where(DonationRecord.donor_id == donor_id)
    
    statement = statement.offset(skip).limit(limit)
    return db.exec(statement).all()

def update_donation_record(db: Session, *, db_obj: DonationRecord, obj_in: DonationRecordUpdate) -> DonationRecord:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def generate_monthly_donations(db: Session, *, masjid_id: uuid.UUID, month: str) -> List[DonationRecord]:
    # 1. Get all active donors for this masjid
    statement = select(Donor).where(
        and_(
            Donor.masjid_id == masjid_id,
            Donor.is_active == True
        )
    )
    donors = db.exec(statement).all()
    
    generated_records = []
    for donor in donors:
        # 2. Check if a record already exists for this donor and month
        existing_statement = select(DonationRecord).where(
            and_(
                DonationRecord.donor_id == donor.id,
                DonationRecord.month == month
            )
        )
        existing = db.exec(existing_statement).first()
        
        if not existing:
            # 3. Create new record
            db_obj = DonationRecord(
                masjid_id=masjid_id,
                donor_id=donor.id,
                month=month,
                pledged_amount=donor.monthly_pledge_amount,
                status="pending"
            )
            db.add(db_obj)
            generated_records.append(db_obj)
            
    db.commit()
    for record in generated_records:
        db.refresh(record)
        
    return generated_records

def verify_donation_payment(
    db: Session, 
    *, 
    db_obj: DonationRecord, 
    obj_in: DonationVerify, 
    user_id: uuid.UUID
) -> DonationRecord:
    # 1. Create linked Income record
    donor = db.get(Donor, db_obj.donor_id)
    income_record = Income(
        masjid_id=db_obj.masjid_id,
        account_id=obj_in.account_id,
        title=f"Monthly Donation - {donor.full_name} ({db_obj.month})",
        amount=obj_in.paid_amount,
        currency=donor.pledge_currency,
        income_date=obj_in.payment_date,
        category="Monthly Donation",
        source=donor.full_name,
        payment_method=obj_in.payment_method,
        reference_number=obj_in.reference_number,
        notes=obj_in.verification_note,
        donor_id=donor.id,
        recorded_by=user_id
    )
    db.add(income_record)
    db.flush()  # To get the income_record.id
    
    # 2. Update DonationRecord status and link
    db_obj.paid_amount = obj_in.paid_amount
    db_obj.payment_date = obj_in.payment_date
    db_obj.payment_method = obj_in.payment_method
    db_obj.reference_number = obj_in.reference_number
    db_obj.verification_note = obj_in.verification_note
    db_obj.verified_by = user_id
    db_obj.income_record_id = income_record.id
    
    if obj_in.paid_amount >= db_obj.pledged_amount:
        db_obj.status = "paid"
    elif obj_in.paid_amount > 0:
        db_obj.status = "partial"
    else:
        db_obj.status = "missed"
        
    db_obj.updated_at = datetime.now(UTC)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
