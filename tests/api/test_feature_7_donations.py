from fastapi.testclient import TestClient
from sqlmodel import Session
from src.core.security import get_password_hash
from src.models.user import User
from src.models.masjid import Masjid
from src.models.account import Account
from src.models.masjid_member import MasjidMember
from datetime import date
import uuid

def test_donor_and_donation_api(client: TestClient, session: Session):
    # 1. Prepare masjid, user, and membership
    masjid = Masjid(name="Feature 7 API Test", slug="f7-api-test", address="Test", city="Test", country="Test", contact_email="f7@test.com")
    session.add(masjid)
    session.commit()
    session.refresh(masjid)
    
    hashed_password = get_password_hash("testpass")
    user = User(
        email="f7-admin@example.com", 
        hashed_password=hashed_password, 
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    member = MasjidMember(masjid_id=masjid.id, user_id=user.id, role="admin", is_active=True)
    session.add(member)
    session.commit()
    
    account = Account(
        masjid_id=masjid.id,
        account_name="API Cash",
        account_type="Cash",
        opening_balance=1000.0,
        created_by=user.id
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    
    # 2. Login
    login_response = client.post(
        "/api/v1/auth/login/access-token",
        data={"username": "f7-admin@example.com", "password": "testpass"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create donor
    donor_data = {
        "full_name": "API Donor",
        "phone": "01711223344",
        "monthly_pledge_amount": 100.0,
        "pledge_start_date": str(date.today()),
        "payment_method": "Cash"
    }
    response = client.post(
        f"/api/v1/donors/?masjid_id={masjid.id}",
        json=donor_data,
        headers=headers
    )
    assert response.status_code == 201
    donor_id = response.json()["id"]
    
    # 4. Generate donations
    gen_data = {"month": "2026-06"}
    response = client.post(
        f"/api/v1/donations/generate?masjid_id={masjid.id}",
        json=gen_data,
        headers=headers
    )
    assert response.status_code == 200
    records = response.json()
    assert len(records) >= 1
    record_id = records[0]["id"]
    
    # 5. Verify donation
    verify_data = {
        "paid_amount": 100.0,
        "payment_date": str(date.today()),
        "payment_method": "Cash",
        "account_id": str(account.id),
        "verification_note": "API Verified"
    }
    response = client.put(
        f"/api/v1/donations/{record_id}/verify?masjid_id={masjid.id}",
        json=verify_data,
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "paid"
