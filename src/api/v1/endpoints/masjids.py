from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from src.db.session import get_session
from src.schemas.masjid import MasjidCreate, MasjidRead, MasjidUpdate
from src.crud import crud_masjid
import uuid

router = APIRouter()

@router.post("/", response_model=MasjidRead, status_code=status.HTTP_201_CREATED)
def register_masjid(masjid: MasjidCreate, session: Session = Depends(get_session)):
    return crud_masjid.masjid.create(session=session, obj_in=masjid)

@router.get("/{masjid_id}", response_model=MasjidRead)
def get_masjid_profile(masjid_id: uuid.UUID, session: Session = Depends(get_session)):
    masjid_obj = crud_masjid.masjid.get(session=session, id=masjid_id)
    if not masjid_obj:
        raise HTTPException(status_code=404, detail="Masjid not found")
    return masjid_obj

@router.patch("/{masjid_id}", response_model=MasjidRead)
def update_masjid_profile(
    masjid_id: uuid.UUID,
    masjid_in: MasjidUpdate,
    session: Session = Depends(get_session)
):
    masjid_obj = crud_masjid.masjid.get(session=session, id=masjid_id)
    if not masjid_obj:
        raise HTTPException(status_code=404, detail="Masjid not found")
    return crud_masjid.masjid.update(session=session, db_obj=masjid_obj, obj_in=masjid_in)

@router.get("/super-admin/analytics")
def super_admin_analytics(session: Session = Depends(get_session)):
    total_masjids = crud_masjid.masjid.count_all(session=session)
    return {
        "total_masjids": total_masjids,
        "active_users": 0, # Placeholder
        "total_transactions": 0 # Placeholder
    }
