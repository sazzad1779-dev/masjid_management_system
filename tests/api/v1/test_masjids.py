import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from src.main import app
from src.db.session import get_session
import uuid

# Setup in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session_override] = get_session_override
    # Since we use get_session as dependency, we need to override it correctly
    from src.db.session import get_session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_register_masjid(client: TestClient):
    response = client.post(
        "/api/v1/masjids/",
        json={
            "name": "Test Masjid",
            "slug": "test-masjid",
            "address": "Test Address",
            "city": "Test City",
            "state": "Test State",
            "country": "Test Country",
            "postal_code": "123456",
            "contact_email": "test@test.com",
            "phone": "1234567890",
            "website": "http://test.com",
            "established_year": 2000,
            "about": "About Test Masjid",
            "currency": "USD",
            "fiscal_year_start_month": "January",
            "primary_color": "#000000",
            "accent_color": "#ffffff",
            "social_media": {},
            "is_public": True,
            "is_active": True
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Masjid"
    assert data["slug"] == "test-masjid"
    assert "id" in data

def test_get_masjid_profile(client: TestClient):
    register_response = client.post(
        "/api/v1/masjids/",
        json={
            "name": "Profile Masjid",
            "slug": "profile-masjid",
            "address": "Address",
            "city": "City",
            "country": "Country",
            "contact_email": "profile@test.com"
        },
    )
    masjid_id = register_response.json()["id"]
    
    response = client.get(f"/api/v1/masjids/{masjid_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Profile Masjid"

def test_update_masjid_profile(client: TestClient):
    register_response = client.post(
        "/api/v1/masjids/",
        json={
            "name": "Update Masjid",
            "slug": "update-masjid",
            "address": "Old Address",
            "city": "Old City",
            "country": "Country",
            "contact_email": "update@test.com"
        },
    )
    masjid_id = register_response.json()["id"]
    
    response = client.patch(
        f"/api/v1/masjids/{masjid_id}",
        json={"address": "New Address", "city": "New City"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == "New Address"
    assert data["city"] == "New City"

def test_super_admin_analytics(client: TestClient):
    # Register a few masjids
    client.post("/api/v1/masjids/", json={"name": "M1", "slug": "m1", "address": "A", "city": "C", "country": "Co", "contact_email": "m1@test.com"})
    client.post("/api/v1/masjids/", json={"name": "M2", "slug": "m2", "address": "A", "city": "C", "country": "Co", "contact_email": "m2@test.com"})
    
    response = client.get("/api/v1/masjids/super-admin/analytics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_masjids"] >= 2
    assert "active_users" in data
    assert "total_transactions" in data
