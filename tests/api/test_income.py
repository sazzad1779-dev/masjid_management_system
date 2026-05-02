from fastapi.testclient import TestClient
from sqlmodel import Session
from src.core.security import get_password_hash
from src.models.user import User
from src.models.masjid import Masjid
from decimal import Decimal
from datetime import date
import uuid

def test_create_income_api(client: TestClient, session: Session):
    # Prepare masjid and user
    masjid = Masjid(name="API Test Masjid", slug="api-test-masjid", address="Test", city="Test", country="Test", contact_email="test@test.com")
    session.add(masjid)
    session.commit()
    session.refresh(masjid)
    
    hashed_password = get_password_hash("testpass")
    user = User(email="income-admin@example.com", hashed_password=hashed_password, role="admin", masjid_id=masjid.id, is_active=True)
    session.add(user)
    session.commit()
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login/access-token",
        data={"username": "income-admin@example.com", "password": "testpass"}
    )
    token = login_response.json()["access_token"]
    
    # Create income
    income_data = {
        "masjid_id": str(masjid.id),
        "title": "API Income",
        "amount": 1000.50,
        "category": "Zakat",
        "income_date": str(date.today()),
        "payment_method": "Cash"
    }
    
    response = client.post(
        "/api/v1/income/",
        json=income_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "API Income"
    assert float(data["amount"]) == 1000.50

def test_read_incomes_api(client: TestClient, session: Session):
    # Prepare masjid and user
    masjid = Masjid(name="Read Test Masjid", slug="read-test-masjid", address="Test", city="Test", country="Test", contact_email="read@test.com")
    session.add(masjid)
    session.commit()
    
    hashed_password = get_password_hash("testpass")
    user = User(email="income-viewer@example.com", hashed_password=hashed_password, role="viewer", masjid_id=masjid.id, is_active=True)
    session.add(user)
    session.commit()
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login/access-token",
        data={"username": "income-viewer@example.com", "password": "testpass"}
    )
    token = login_response.json()["access_token"]
    
    # Read incomes
    response = client.get(
        f"/api/v1/income/?masjid_id={masjid.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_weekly_summary_api(client: TestClient, session: Session):
    # Prepare masjid and user
    masjid = Masjid(name="Weekly Test Masjid", slug="weekly-test-masjid", address="Test", city="Test", country="Test", contact_email="weekly@test.com")
    session.add(masjid)
    session.commit()
    
    hashed_password = get_password_hash("testpass")
    user = User(email="weekly-admin@example.com", hashed_password=hashed_password, role="admin", masjid_id=masjid.id, is_active=True)
    session.add(user)
    session.commit()
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login/access-token",
        data={"username": "weekly-admin@example.com", "password": "testpass"}
    )
    token = login_response.json()["access_token"]
    
    # Get weekly summary
    today = date.today()
    response = client.get(
        f"/api/v1/income/weekly?masjid_id={masjid.id}&start_date={today}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["masjid_id"] == str(masjid.id)
    assert "total_income" in data
