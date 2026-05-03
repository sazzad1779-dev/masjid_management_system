import uuid
from typing import List, Optional
from sqlmodel import Session, select
from src.models.donor import Donor
from src.schemas.donor import DonorCreate, DonorUpdate

def create_donor(db: Session, *, obj_in: DonorCreate, masjid_id: uuid.UUID, user_id: uuid.UUID) -> Donor:
    db_obj = Donor(
        **obj_in.model_dump(),
        masjid_id=masjid_id,
        created_by=user_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_donor(db: Session, donor_id: uuid.UUID) -> Optional[Donor]:
    return db.get(Donor, donor_id)

def get_donors(db: Session, *, masjid_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Donor]:
    statement = select(Donor).where(Donor.masjid_id == masjid_id).offset(skip).limit(limit)
    return db.exec(statement).all()

def get_donor_by_user_id(db: Session, user_id: uuid.UUID) -> Optional[Donor]:
    statement = select(Donor).where(Donor.user_id == user_id)
    return db.exec(statement).first()

def update_donor(db: Session, *, db_obj: Donor, obj_in: DonorUpdate) -> Donor:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def deactivate_donor(db: Session, *, donor_id: uuid.UUID) -> Optional[Donor]:
    db_obj = db.get(Donor, donor_id)
    if db_obj:
        db_obj.is_active = False
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
    return db_obj

def activate_donor(db: Session, *, donor_id: uuid.UUID) -> Optional[Donor]:
    db_obj = db.get(Donor, donor_id)
    if db_obj:
        db_obj.is_active = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
    return db_obj

def hard_delete_donor(db: Session, *, donor_id: uuid.UUID) -> Optional[Donor]:
    db_obj = db.get(Donor, donor_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
