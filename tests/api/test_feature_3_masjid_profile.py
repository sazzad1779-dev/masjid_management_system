import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from src.main import app
from src.db.session import engine, init_db
from src.models.masjid import Masjid
import uuid

client = TestClient(app)

@pytest.fixture(name="session")
def session_fixture():
    init_db()
    with Session(engine) as session:
        yield session

def test_create_masjid_with_full_profile(session: Session):
    masjid_name = "Test Masjid Profile"
    masjid_slug = f"test-masjid-{uuid.uuid4().hex[:6]}"
    
    response = client.post(
        "/api/v1/masjids/",
        json={
            "name": masjid_name,
            "slug": masjid_slug,
            "address": "123 Test St",
            "city": "Test City",
            "country": "Test Country",
            "contact_email": "test@masjid.com",
            "currency": "USD",
            "fiscal_year_start_month": "January",
            "friday_jumuah_time": "1:15 PM",
            "notification_settings": {"email": True},
            "default_categories": {"income": ["Donation"]},
            "primary_color": "#123456",
            "accent_color": "#654321"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == masjid_name
    assert data["friday_jumuah_time"] == "1:15 PM"
    assert data["notification_settings"] == {"email": True}
    assert data["default_categories"] == {"income": ["Donation"]}

def test_get_masjid_profile(session: Session):
    # First create a masjid
    masjid = Masjid(
        name="Get Profile Test",
        slug="get-profile-test",
        address="Test Address",
        city="Test City",
        country="Test Country",
        contact_email="get@test.com",
        friday_jumuah_time="1:45 PM"
    )
    session.add(masjid)
    session.commit()
    session.refresh(masjid)
    
    response = client.get(f"/api/v1/masjids/{masjid.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Get Profile Test"
    assert data["friday_jumuah_time"] == "1:45 PM"

def test_update_masjid_profile(session: Session):
    # First create a masjid
    masjid = Masjid(
        name="Update Profile Test",
        slug="update-profile-test",
        address="Test Address",
        city="Test City",
        country="Test Country",
        contact_email="update@test.com",
    )
    session.add(masjid)
    session.commit()
    session.refresh(masjid)
    
    # Update it
    response = client.patch(
        f"/api/v1/masjids/{masjid.id}",
        json={
            "name": "Updated Masjid Name",
            "friday_jumuah_time": "2:00 PM",
            "notification_settings": {"sms": True},
            "primary_color": "#00FF00"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Masjid Name"
    assert data["friday_jumuah_time"] == "2:00 PM"
    assert data["notification_settings"] == {"sms": True}
    assert data["primary_color"] == "#00FF00"
