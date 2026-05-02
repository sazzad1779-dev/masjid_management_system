import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from src.core.config import settings
from src.models.user import User
from src.models.masjid import Masjid
from src.models.masjid_member import MasjidMember
from src.core.security import verify_password
import jwt

def test_login_access_token(client: TestClient, session: Session):
    # Ensure seeder-like setup in test DB if conftest creates clean DB
    # (Actually conftest.py in this project creates clean DB per session fixture)
    
    # Create test user
    from src.core.security import get_password_hash
    user = User(email="test@example.com", hashed_password=get_password_hash("password123"))
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Create masjid and membership
    masjid = Masjid(name="Test Masjid", slug="test-masjid", address="123", city="Dhaka", country="BD", contact_email="t@t.com")
    session.add(masjid)
    session.commit()
    session.refresh(masjid)
    
    membership = MasjidMember(user_id=user.id, masjid_id=masjid.id, role="admin")
    session.add(membership)
    session.commit()

    # Test login
    login_data = {
        "username": "test@example.com",
        "password": "password123",
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login/access-token", data=login_data)
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"
    
    # Verify token payload
    payload = jwt.decode(tokens["access_token"], settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == str(user.id)
    assert payload["role"] == "admin"
    assert payload["masjid_id"] == str(masjid.id)

def test_refresh_token(client: TestClient, session: Session):
    from src.core.security import get_password_hash, create_refresh_token
    user = User(email="refresh@example.com", hashed_password=get_password_hash("password123"))
    session.add(user)
    session.commit()
    session.refresh(user)
    
    refresh_token = create_refresh_token(subject=user.id)
    
    # Test refresh
    r = client.post(f"{settings.API_V1_STR}/auth/refresh?refresh_token={refresh_token}")
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens
    assert tokens["refresh_token"] == refresh_token

def test_rbac_income_access(client: TestClient, session: Session):
    from src.core.security import get_password_hash, create_access_token
    
    # Create admin user
    admin_user = User(email="admin_rbac@example.com", hashed_password=get_password_hash("pass"))
    session.add(admin_user)
    
    # Create viewer user
    viewer_user = User(email="viewer_rbac@example.com", hashed_password=get_password_hash("pass"))
    session.add(viewer_user)
    
    masjid = Masjid(name="M", slug="m", address="A", city="C", country="B", contact_email="e@e.com")
    session.add(masjid)
    session.commit()
    session.refresh(admin_user)
    session.refresh(viewer_user)
    session.refresh(masjid)
    
    session.add(MasjidMember(user_id=admin_user.id, masjid_id=masjid.id, role="admin"))
    session.add(MasjidMember(user_id=viewer_user.id, masjid_id=masjid.id, role="viewer"))
    session.commit()
    
    # Admin Token
    admin_token = create_access_token(subject=admin_user.id, role="admin", masjid_id=masjid.id)
    # Viewer Token
    viewer_token = create_access_token(subject=viewer_user.id, role="viewer", masjid_id=masjid.id)
    
    # Test Create Income (should be allowed for admin, denied for viewer)
    income_data = {
        "title": "Donation",
        "amount": 100,
        "currency": "USD",
        "income_date": "2024-05-01",
        "category": "Zakath",
        "payment_method": "Cash",
        "masjid_id": str(masjid.id)
    }
    
    # Viewer try to create
    r = client.post(
        f"{settings.API_V1_STR}/income/",
        json=income_data,
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert r.status_code == 403
    
    # Admin try to create
    r = client.post(
        f"{settings.API_V1_STR}/income/",
        json=income_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert r.status_code == 201
