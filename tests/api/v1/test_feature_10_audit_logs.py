import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from src.core.config import settings
from src.models.audit_log import AuditLog
from src.core.security import create_access_token
from src.models.user import User
from src.models.masjid import Masjid
from src.models.account import Account
from src.models.masjid_member import MasjidMember
import uuid
from datetime import date

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

@pytest.fixture
def test_data(session: Session):
    user_id = uuid.uuid4()
    masjid_id = uuid.uuid4()
    account_id = uuid.uuid4()
    
    user = User(id=user_id, email="audit_admin@test.com", full_name="Audit Admin", hashed_password="hashed_password", is_active=True)
    session.add(user)
    masjid = Masjid(id=masjid_id, name="Audit Masjid", slug="audit-masjid", address="Test", city="Test", country="Test", contact_email="audit_admin@test.com")
    session.add(masjid)
    session.commit()
    
    session.add(MasjidMember(user_id=user_id, masjid_id=masjid_id, role="admin"))
    
    account = Account(
        id=account_id,
        masjid_id=masjid_id,
        account_name="Audit Cash Box",
        account_type="Cash",
        opening_balance=10000,
        opening_date=date(2026, 1, 1),
        created_by=user_id
    )
    session.add(account)
    session.commit()
    
    return {
        "user_id": user_id,
        "masjid_id": masjid_id,
        "account_id": account_id,
        "user": user,
        "masjid": masjid,
        "account": account
    }

def test_read_audit_logs_as_admin(client: TestClient, session: Session, test_data: dict):
    # Seed an audit log manually
    log = AuditLog(
        masjid_id=test_data["masjid_id"],
        user_id=test_data["user_id"],
        user_name=test_data["user"].email,
        action="test_action",
        entity_type="test_entity",
        details="Test details"
    )
    session.add(log)
    session.commit()
    
    headers = get_admin_token_headers(str(test_data["user_id"]), str(test_data["masjid_id"]))
    
    response = client.get(
        f"{settings.API_V1_STR}/audit-logs/masjids/{test_data['masjid_id']}",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["action"] == "test_action"

def test_income_creates_audit_log(client: TestClient, session: Session, test_data: dict):
    income_data = {
        "title": "Donation Collection",
        "amount": 1000,
        "currency": "BDT",
        "income_date": "2026-05-01",
        "category": "General Donation",
        "payment_method": "Cash",
        "masjid_id": str(test_data["masjid_id"]),
        "account_id": str(test_data["account_id"])
    }
    
    headers = get_admin_token_headers(str(test_data["user_id"]), str(test_data["masjid_id"]))
    
    response = client.post(
        f"{settings.API_V1_STR}/income/",
        headers=headers,
        json=income_data,
    )
    assert response.status_code == 201
    income_id = response.json()["id"]
    
    # Check audit logs
    response = client.get(
        f"{settings.API_V1_STR}/audit-logs/masjids/{test_data['masjid_id']}",
        params={"entity_type": "income"},
        headers=headers,
    )
    assert response.status_code == 200
    logs = response.json()
    assert any(log["action"] == "create" and log["entity_id"] == income_id for log in logs)

def test_expense_creates_audit_log(client: TestClient, session: Session, test_data: dict):
    expense_data = {
        "title": "Utility Bill",
        "amount": 500,
        "currency": "BDT",
        "expense_date": "2026-05-01",
        "category": "Utilities",
        "payment_method": "Cash",
        "masjid_id": str(test_data["masjid_id"]),
        "account_id": str(test_data["account_id"])
    }
    
    headers = get_admin_token_headers(str(test_data["user_id"]), str(test_data["masjid_id"]))
    
    response = client.post(
        f"{settings.API_V1_STR}/expense/",
        headers=headers,
        json=expense_data,
    )
    assert response.status_code == 201
    expense_id = response.json()["id"]
    
    # Check audit logs
    response = client.get(
        f"{settings.API_V1_STR}/audit-logs/masjids/{test_data['masjid_id']}",
        params={"entity_type": "expense"},
        headers=headers,
    )
    assert response.status_code == 200
    logs = response.json()
    assert any(log["action"] == "create" and log["entity_id"] == expense_id for log in logs)

def test_login_creates_audit_log(client: TestClient, session: Session, test_data: dict):
    # We need to use a real user password for authenticate_user to work if it hashes
    # But for tests we usually mock or use a known simple password if hashed_password is just the string
    # Assuming authenticate_user uses plain text comparison in this simple setup or I should use a proper hash
    from src.core.security import get_password_hash
    test_data["user"].hashed_password = get_password_hash("testpass")
    session.add(test_data["user"])
    session.commit()
    
    login_data = {
        "username": "audit_admin@test.com",
        "password": "testpass"
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/auth/login/access-token",
        data=login_data,
    )
    assert response.status_code == 200
    
    headers = get_admin_token_headers(str(test_data["user_id"]), str(test_data["masjid_id"]))
    
    # Check audit logs
    response = client.get(
        f"{settings.API_V1_STR}/audit-logs/masjids/{test_data['masjid_id']}",
        params={"action": "login"},
        headers=headers,
    )
    assert response.status_code == 200
    logs = response.json()
    assert any(log["action"] == "login" for log in logs)

def test_update_donor_creates_audit_log(client: TestClient, session: Session, test_data: dict):
    # Create donor first
    from src.models.donor import Donor
    donor = Donor(
        masjid_id=test_data["masjid_id"],
        full_name="Test Donor",
        phone="123456789",
        monthly_pledge_amount=1000,
        pledge_currency="BDT",
        pledge_start_date=date(2026, 1, 1),
        payment_method="Cash",
        created_by=test_data["user_id"]
    )
    session.add(donor)
    session.commit()
    session.refresh(donor)
    
    headers = get_admin_token_headers(str(test_data["user_id"]), str(test_data["masjid_id"]))
    
    update_data = {"full_name": "Updated Donor Name"}
    response = client.put(
        f"{settings.API_V1_STR}/donors/{donor.id}",
        params={"masjid_id": str(test_data["masjid_id"])},
        headers=headers,
        json=update_data,
    )
    assert response.status_code == 200
    
    # Check audit logs
    response = client.get(
        f"{settings.API_V1_STR}/audit-logs/masjids/{test_data['masjid_id']}",
        params={"entity_type": "donor", "action": "update"},
        headers=headers,
    )
    assert response.status_code == 200
    logs = response.json()
    assert any(log["action"] == "update" and log["entity_id"] == str(donor.id) for log in logs)
    # Check old/new values in detail log?
    log = next(log for log in logs if log["entity_id"] == str(donor.id))
    assert log["old_value"]["full_name"] == "Test Donor"
    assert log["new_value"]["full_name"] == "Updated Donor Name"
