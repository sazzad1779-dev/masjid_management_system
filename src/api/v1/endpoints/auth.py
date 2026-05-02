from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from src.core.config import settings
from src.core.security import create_access_token, create_refresh_token
from src.crud import user as crud_user
from src.schemas.user import Token, UserRead, UserCreate, TokenPayload
from src.api.dependencies import get_current_user
from src.db.session import get_session
from src.models.user import User
import jwt

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_session), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = crud_user.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    # Get primary masjid_id and role from memberships if they exist
    masjid_id = None
    role = "viewer"
    if user.memberships:
        # For simplicity, pick the first active membership
        for membership in user.memberships:
            if membership.is_active:
                masjid_id = membership.masjid_id
                role = membership.role
                break

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        role=role,
        masjid_id=masjid_id,
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }

@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_session)
) -> Any:
    """
    Refresh access token.
    """
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.type != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")
    except (jwt.PyJWTError, Exception):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user = crud_user.get_user(db, user_id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    masjid_id = None
    role = "viewer"
    if user.memberships:
        for membership in user.memberships:
            if membership.is_active:
                masjid_id = membership.masjid_id
                role = membership.role
                break

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        role=role,
        masjid_id=masjid_id,
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token, # Reuse refresh token or rotate it
    }

@router.post("/forgot-password")
def forgot_password(email: str) -> Any:
    """
    Stub for forgot password.
    """
    return {"message": "Password reset email sent if user exists"}

@router.post("/reset-password")
def reset_password(token: str, new_password: str) -> Any:
    """
    Stub for reset password.
    """
    return {"message": "Password reset successful"}

@router.post("/signup", response_model=UserRead)
def create_user_signup(
    *,
    db: Session = Depends(get_session),
    user_in: UserCreate,
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud_user.create_user(db, user_in=user_in)
    return user

@router.get("/me", response_model=UserRead)
def read_user_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user.
    """
    return current_user
