import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.core.config import settings
from src.models.notification import Notification
from src.core.security import create_access_token

def get_admin_token_headers(user_id: str, masjid_id: str) -> dict:
    access_token = create_access_token(
        subject=user_id,
        role="admin",
        masjid_id=masjid_id
    )
    return {"Authorization": f"Bearer {access_token}"}

def get_superadmin_token_headers(user_id: str) -> dict:
    access_token = create_access_token(
        subject=user_id,
        role="super_admin"
    )
    return {"Authorization": f"Bearer {access_token}"}

def test_read_notifications(client: TestClient, session: Session):
    # Seed a notification manually
    from src.models.user import User
    from src.models.masjid import Masjid
    from sqlmodel import select
    
    # 1. Setup Data
    user = User(email="test@example.com", hashed_password="hashed_password", is_active=True)
    session.add(user)
    masjid = Masjid(name="Test Masjid", slug="test-masjid", address="Test", city="Test", country="Test", contact_email="test@example.com")
    session.add(masjid)
    session.commit()
    session.refresh(user)
    session.refresh(masjid)
    
    n = Notification(
        user_id=user.id,
        masjid_id=masjid.id,
        type="test_type",
        title="Test Notification",
        body="Test Body",
        is_read=False
    )
    session.add(n)
    session.commit()
    session.refresh(n)
    
    # 2. Get headers
    headers = get_superadmin_token_headers(str(user.id))
    
    # 3. Test
    response = client.get(
        f"{settings.API_V1_STR}/notifications/",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "Test Notification"

def test_mark_notification_as_read(client: TestClient, session: Session):
    from src.models.user import User
    from src.models.masjid import Masjid
    
    user = User(email="test2@example.com", hashed_password="hashed_password", is_active=True)
    session.add(user)
    masjid = Masjid(name="Test Masjid 2", slug="test-masjid-2", address="Test", city="Test", country="Test", contact_email="test2@example.com")
    session.add(masjid)
    session.commit()
    session.refresh(user)
    session.refresh(masjid)
    
    n = Notification(
        user_id=user.id,
        masjid_id=masjid.id,
        type="test_type",
        title="Unread Notification",
        body="Test Body",
        is_read=False
    )
    session.add(n)
    session.commit()
    session.refresh(n)
    
    headers = get_superadmin_token_headers(str(user.id))
    
    response = client.put(
        f"{settings.API_V1_STR}/notifications/{n.id}/read",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is True

def test_mark_all_read(client: TestClient, session: Session):
    from src.models.user import User
    user = User(email="test3@example.com", hashed_password="hashed_password", is_active=True)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    headers = get_superadmin_token_headers(str(user.id))
    
    response = client.put(
        f"{settings.API_V1_STR}/notifications/read-all",
        headers=headers,
    )
    assert response.status_code == 200
    assert "Marked" in response.json()["message"]

def test_income_creates_notification(client: TestClient, session: Session):
    # Create income and check if notification is created for admin
    from src.models.user import User
    from src.models.masjid import Masjid
    from src.models.account import Account
    from src.models.masjid_member import MasjidMember
    import uuid
    from datetime import date
    
    # 1. Setup Data with explicit IDs
    user_id = uuid.uuid4()
    masjid_id = uuid.uuid4()
    account_id = uuid.uuid4()
    
    user = User(id=user_id, email="admin@test.com", hashed_password="hashed_password", is_active=True)
    session.add(user)
    masjid = Masjid(id=masjid_id, name="Income Masjid", slug="income-masjid", address="Test", city="Test", country="Test", contact_email="admin@test.com")
    session.add(masjid)
    session.commit()
    
    # Add as admin
    session.add(MasjidMember(user_id=user_id, masjid_id=masjid_id, role="admin"))
    
    account = Account(
        id=account_id,
        masjid_id=masjid_id,
        account_name="Cash Box",
        account_type="Cash",
        opening_balance=0,
        opening_date=date(2026, 1, 1)
    )
    session.add(account)
    session.commit()
    
    income_data = {
        "title": "Friday Collection",
        "amount": 1000,
        "currency": "BDT",
        "income_date": "2026-05-01",
        "category": "Friday Jumu'ah Collection",
        "payment_method": "Cash",
        "masjid_id": str(masjid_id),
        "account_id": str(account_id)
    }
    
    headers = get_admin_token_headers(str(user_id), str(masjid_id))
    
    response = client.post(
        f"{settings.API_V1_STR}/income/",
        headers=headers,
        json=income_data,
    )
    assert response.status_code == 201
    
    # Check notifications for admin
    response = client.get(
        f"{settings.API_V1_STR}/notifications/",
        headers=headers,
    )
    assert response.status_code == 200
    notifications = response.json()
    assert any(n["type"] == "income_recorded" for n in notifications)
