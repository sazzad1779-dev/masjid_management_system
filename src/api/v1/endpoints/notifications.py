from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from src.api import dependencies as deps
from src.crud import notification as notification_crud
from src.schemas import notification as notification_schema
from src.models.user import User
from src.models.notification import Notification

import uuid

router = APIRouter()

@router.get("/", response_model=List[notification_schema.NotificationRead])
def read_notifications(
    db: Session = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
    is_read: Optional[bool] = Query(None),
):
    """
    Retrieve notifications for current user.
    """
    notifications = notification_crud.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit, is_read=is_read
    )
    return notifications

@router.put("/{notification_id}/read", response_model=notification_schema.NotificationRead)
def mark_notification_as_read(
    notification_id: uuid.UUID,
    db: Session = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Mark a notification as read.
    """
    statement = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    )
    notification = db.exec(statement).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return notification_crud.update(
        db, db_obj=notification, obj_in={"is_read": True}
    )

@router.put("/read-all")
def mark_all_notifications_as_read(
    db: Session = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Mark all notifications as read for the current user.
    """
    count = notification_crud.mark_all_as_read(db, user_id=current_user.id)
    return {"message": f"Marked {count} notifications as read"}
