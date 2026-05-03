from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from src.db.session import get_session
from src.schemas.masjid import MasjidCreate, MasjidRead, MasjidUpdate
from src.crud import crud_masjid
from src.api.dependencies import get_current_user
from src.models.user import User
import uuid

router = APIRouter()

@router.get("/me", response_model=MasjidRead)
def read_masjid_me(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get current masjid profile based on token.
    """
    masjid_id = getattr(current_user, "_token_masjid_id", None)
    if not masjid_id:
        raise HTTPException(status_code=400, detail="User is not associated with a masjid")
    
    masjid_obj = crud_masjid.masjid.get(session=session, id=uuid.UUID(str(masjid_id)))
    if not masjid_obj:
        raise HTTPException(status_code=404, detail="Masjid not found")
    return masjid_obj

@router.patch("/me", response_model=MasjidRead)
def update_masjid_me(
    *,
    session: Session = Depends(get_session),
    masjid_in: MasjidUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update current masjid profile based on token.
    """
    masjid_id = getattr(current_user, "_token_masjid_id", None)
    if not masjid_id:
        raise HTTPException(status_code=400, detail="User is not associated with a masjid")
        
    masjid_obj = crud_masjid.masjid.get(session=session, id=uuid.UUID(str(masjid_id)))
    if not masjid_obj:
        raise HTTPException(status_code=404, detail="Masjid not found")
        
    # Check permissions
    role = getattr(current_user, "_token_role", "viewer")
    if role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return crud_masjid.masjid.update(session=session, db_obj=masjid_obj, obj_in=masjid_in)

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
    from src.models.user import User
    from src.models.income import Income
    from src.models.masjid import Masjid
    from sqlmodel import select, func
    
    total_masjids = session.exec(select(func.count(Masjid.id))).one()
    active_users = session.exec(select(func.count(User.id)).where(User.is_active == True)).one()
    total_transactions = session.exec(select(func.count(Income.id))).one()
    
    return {
        "total_masjids": total_masjids,
        "active_users": active_users,
        "total_transactions": total_transactions
    }
