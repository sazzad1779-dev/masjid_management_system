from typing import Optional
from sqlmodel import Session, select
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.core.security import get_password_hash, verify_password

def get_user(db: Session, user_id: str) -> Optional[User]:
    return db.get(User, user_id)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return db.exec(statement).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    db_obj = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        masjid_id=user_in.masjid_id,
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

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
