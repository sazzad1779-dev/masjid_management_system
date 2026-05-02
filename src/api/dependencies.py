from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
import jwt
from jwt.exceptions import InvalidTokenError

from src.core.config import settings
from src.models.user import User
from src.schemas.user import TokenPayload
from src.db.session import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token")

def get_current_user(db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenPayload(**payload)
        if not token_data.sub:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
        
    import uuid
    user = db.get(User, uuid.UUID(token_data.sub))
    if not user:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    # Store the token data (role, masjid_id) on the user object using private attributes
    # to avoid SQLModel/SQLAlchemy trying to persist them to the DB.
    user._token_masjid_id = token_data.masjid_id
    user._token_role = token_data.role
    
    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        # Check if user has global super_admin or admin role in the token context
        # In a real system, we might check a user.is_super_admin flag
        # For now, we trust the role in the token if it matches
        
        user_role = getattr(user, "_token_role", "viewer")
        user_masjid_id = getattr(user, "_token_masjid_id", None)
        
        if user_role == "super_admin":
            return user
            
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return user
