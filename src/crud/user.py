from typing import Optional
from sqlmodel import Session, select
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.core.security import get_password_hash, verify_password

from src.models.masjid_member import MasjidMember

import uuid

def get_user(db: Session, user_id: str) -> Optional[User]:
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)
    return db.get(User, user_id)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return db.exec(statement).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    db_obj = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_active=user_in.is_active,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User:
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        password = update_data.pop("password")
        update_data["hashed_password"] = get_password_hash(password)
        
    for field, value in update_data.items():
        setattr(db_user, field, value)
        
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def add_user_to_masjid(db: Session, user_id: str, masjid_id: str, role: str = "viewer") -> MasjidMember:
    from src.services.notification import NotificationService
    db_obj = MasjidMember(
        user_id=user_id,
        masjid_id=masjid_id,
        role=role
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # Trigger notification
    NotificationService.notify_user_invitation(db, db_obj)
    
    return db_obj

def update_masjid_member_role(db: Session, member_id: str, role: str) -> Optional[MasjidMember]:
    from src.services.notification import NotificationService
    db_obj = db.get(MasjidMember, member_id)
    if db_obj:
        db_obj.role = role
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Trigger notification
        NotificationService.notify_role_change(db, db_obj)
    return db_obj

def get_user_masjid_membership(db: Session, user_id: str, masjid_id: str) -> Optional[MasjidMember]:
    statement = select(MasjidMember).where(
        MasjidMember.user_id == user_id,
        MasjidMember.masjid_id == masjid_id
    )
    return db.exec(statement).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
