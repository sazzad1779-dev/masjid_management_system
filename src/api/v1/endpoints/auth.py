from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from src.core.config import settings
from src.core.security import create_access_token, create_refresh_token
from src.crud import user as crud_user
from src.schemas.user import Token, UserRead, UserCreate, UserSignup, TokenPayload, UserInvite
from src.api.dependencies import get_current_user, RoleChecker
from src.db.session import get_session
from src.models.user import User
from src.services.audit_log import AuditLogService
import jwt
import uuid
from typing import Any, List

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    request: Request,
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
    
    # Audit Log
    AuditLogService.log_action(
        db=db,
        user_id=user.id,
        user_name=user.email,
        action="login",
        entity_type="user",
        masjid_id=masjid_id,
        entity_id=user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
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
    request: Request,
    db: Session = Depends(get_session),
    user_in: UserSignup,
) -> Any:
    """
    Create new user and their institution, without the need to be logged in.
    """
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Create the user
    user_create = UserCreate(email=user_in.email, password=user_in.password)
    user = crud_user.create_user(db, user_in=user_create)

    # Create the masjid
    from src.schemas.masjid import MasjidCreate
    from src.crud.crud_masjid import masjid as crud_masjid
    import re

    slug = re.sub(r'[^a-z0-9]+', '-', user_in.institution_name.lower()).strip('-')

    masjid_in = MasjidCreate(
        name=user_in.institution_name,
        slug=slug,
        address="Please update address",
        city="Please update city",
        country="Please update country",
        contact_email=user_in.email
    )
    new_masjid = crud_masjid.create(db, obj_in=masjid_in)

    # Link user to masjid as super_admin
    crud_user.add_user_to_masjid(db, user_id=user.id, masjid_id=new_masjid.id, role="super_admin")
    
    # Audit Log
    AuditLogService.log_action(
        db=db,
        user_id=user.id,
        user_name=user.email,
        action="signup",
        entity_type="user_and_masjid",
        masjid_id=new_masjid.id,
        entity_id=user.id,
        new_value={"masjid_name": user_in.institution_name, "admin_name": user_in.admin_name},
    )
    
    # Refresh user to load relationships
    db.refresh(user)
    return user

@router.get("/me", response_model=UserRead)
def read_user_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.get("/users", response_model=List[UserRead])
def read_users(
    *,
    db: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(RoleChecker(["super_admin", "admin", "committee"]))
) -> Any:
    """
    Retrieve users for a given masjid.
    """
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)
    
    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    users = crud_user.get_users_by_masjid(db, masjid_id=masjid_id, skip=skip, limit=limit)
    return users

@router.post("/invite", response_model=UserRead)
def invite_user(
    *,
    db: Session = Depends(get_session),
    request: Request,
    invite_in: UserInvite,
    current_user: User = Depends(RoleChecker(["super_admin", "admin"]))
) -> Any:
    """
    Invite a user to a masjid.
    """
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)
    
    if current_role != "super_admin" and str(current_masjid_id) != str(invite_in.masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    # Check if user exists
    user = crud_user.get_user_by_email(db, email=invite_in.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Users must register first in this version.")
    
    # Check if already a member
    membership = crud_user.get_user_masjid_membership(db, user_id=user.id, masjid_id=invite_in.masjid_id)
    if membership:
        raise HTTPException(status_code=400, detail="User is already a member of this masjid")
        
    membership = crud_user.add_user_to_masjid(db, user_id=user.id, masjid_id=invite_in.masjid_id, role=invite_in.role)
    
    # Audit Log
    AuditLogService.log_action(
        db=db,
        user_id=current_user.id,
        user_name=current_user.email,
        action="invite",
        entity_type="masjid_member",
        masjid_id=invite_in.masjid_id,
        entity_id=membership.id,
        new_value={"user_id": str(user.id), "role": invite_in.role},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return user
