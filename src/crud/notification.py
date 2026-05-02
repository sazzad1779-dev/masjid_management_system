from typing import List, Optional
from sqlmodel import Session, select
from src.models.notification import Notification
from src.schemas.notification import NotificationCreate, NotificationUpdate

def create(db: Session, *, obj_in: NotificationCreate) -> Notification:
    db_obj = Notification.model_validate(obj_in)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_multi_by_user(
    db: Session, *, user_id: str, skip: int = 0, limit: int = 100, is_read: Optional[bool] = None
) -> List[Notification]:
    statement = select(Notification).where(Notification.user_id == user_id)
    if is_read is not None:
        statement = statement.where(Notification.is_read == is_read)
    return db.exec(statement.order_by(Notification.created_at.desc()).offset(skip).limit(limit)).all()

def update(
    db: Session, *, db_obj: Notification, obj_in: NotificationUpdate | dict
) -> Notification:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)
            
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def mark_all_as_read(db: Session, *, user_id: str) -> int:
    statement = select(Notification).where(
        Notification.user_id == user_id, 
        Notification.is_read == False
    )
    results = db.exec(statement).all()
    for n in results:
        n.is_read = True
        db.add(n)
    db.commit()
    return len(results)
