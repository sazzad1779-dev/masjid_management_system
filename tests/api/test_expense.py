import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.core.security import get_password_hash
from src.models.user import User
from src.models.masjid import Masjid
from src.models.masjid_member import MasjidMember
from decimal import Decimal
from datetime import date
import uuid

def prepare_test_data(session: Session, client: TestClient, role: str = "admin", email: str = "test@example.com"):
    # Clear existing to be safe
    masjid = Masjid(name="Test Masjid", slug=f"test-masjid-{uuid.uuid4()}", address="Test", city="Test", country="Test", contact_email=f"test-{uuid.uuid4()}@test.com")
    session.add(masjid)
    session.commit()
    session.refresh(masjid)
    
    hashed_password = get_password_hash("testpass")
    user = User(email=email, hashed_password=hashed_password, is_active=True)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Create membership (CRITICAL for role in token)
    membership = MasjidMember(masjid_id=masjid.id, user_id=user.id, role=role, is_active=True)
    session.add(membership)
    session.commit()
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login/access-token",
        data={"username": email, "password": "testpass"}
    )
    token_data = login_response.json()
    if "access_token" not in token_data:
        print(f"Login failed: {token_data}")
        raise ValueError("Login failed")
    token = token_data["access_token"]
    return masjid.id, token, user.id

def test_create_expense(client: TestClient, session: Session):
    masjid_id, token, _ = prepare_test_data(session, client)
    
    response = client.post(
        "/api/v1/expense/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "masjid_id": str(masjid_id),
            "title": "Test Expense",
            "amount": 100.00,
            "category": "Utilities",
            "expense_date": str(date.today()),
            "payment_method": "Cash"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Expense"
    assert float(data["amount"]) == 100.00

def test_read_expenses(client: TestClient, session: Session):
    masjid_id, token, _ = prepare_test_data(session, client)
    
    # Create one first
    client.post(
        "/api/v1/expense/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "masjid_id": str(masjid_id),
            "title": "Expense 1",
            "amount": 50.00,
            "category": "Maintenance",
            "expense_date": str(date.today()),
            "payment_method": "Cash"
        }
    )
    
    response = client.get(
        f"/api/v1/expense/?masjid_id={masjid_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(item["title"] == "Expense 1" for item in data)

def test_get_expense_summary(client: TestClient, session: Session):
    masjid_id, token, _ = prepare_test_data(session, client)
    today = date.today()
    response = client.get(
        f"/api/v1/expense/summary?masjid_id={masjid_id}&year={today.year}&month={today.month}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_expense" in data

def test_update_expense(client: TestClient, session: Session):
    masjid_id, token, _ = prepare_test_data(session, client)
    
    # Create one
    res = client.post(
        "/api/v1/expense/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "masjid_id": str(masjid_id),
            "title": "Old Title",
            "amount": 10.00,
            "category": "Other",
            "expense_date": str(date.today())
        }
    )
    expense_id = res.json()["id"]
    
    # Update it
    response = client.patch(
        f"/api/v1/expense/{expense_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "New Title"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

def test_delete_expense(client: TestClient, session: Session):
    masjid_id, token, _ = prepare_test_data(session, client)
    
    # Create one
    res = client.post(
        "/api/v1/expense/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "masjid_id": str(masjid_id),
            "title": "To Delete",
            "amount": 20.00,
            "category": "Other",
            "expense_date": str(date.today())
        }
    )
    expense_id = res.json()["id"]
    
    # Delete it
    response = client.delete(
        f"/api/v1/expense/{expense_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_deleted"] is True

def test_expense_rbac_committee(client: TestClient, session: Session):
    masjid_id, token, _ = prepare_test_data(session, client, role="committee", email="comm@test.com")
    
    # Committee should be able to create
    response = client.post(
        "/api/v1/expense/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "masjid_id": str(masjid_id),
            "title": "Committee Expense",
            "amount": 30.00,
            "category": "Other",
            "expense_date": str(date.today())
        }
    )
    assert response.status_code == 201

def test_expense_rbac_delete_denied(client: TestClient, session: Session):
    masjid_id, admin_token, _ = prepare_test_data(session, client, role="admin", email="admin-rbac@test.com")
    
    # Create an expense as admin
    res = client.post(
        "/api/v1/expense/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "masjid_id": str(masjid_id),
            "title": "Admin Expense",
            "amount": 100.00,
            "category": "Other",
            "expense_date": str(date.today())
        }
    )
    expense_id = res.json()["id"]
    
    # Get a committee user for the SAME masjid
    hashed_password = get_password_hash("testpass")
    comm_user = User(email="comm-rbac@test.com", hashed_password=hashed_password, is_active=True)
    session.add(comm_user)
    session.commit()
    
    membership = MasjidMember(masjid_id=masjid_id, user_id=comm_user.id, role="committee", is_active=True)
    session.add(membership)
    session.commit()
    
    # Login as committee
    login_response = client.post(
        "/api/v1/auth/login/access-token",
        data={"username": "comm-rbac@test.com", "password": "testpass"}
    )
    comm_token = login_response.json()["access_token"]
    
    # Committee should NOT be able to delete
    response = client.delete(
        f"/api/v1/expense/{expense_id}",
        headers={"Authorization": f"Bearer {comm_token}"}
    )
    assert response.status_code == 403
