from fastapi.testclient import TestClient
from sqlmodel import Session
from src.core.security import get_password_hash
from src.models.user import User

def test_signup(client: TestClient):
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "newuser@example.com", "password": "password123", "role": "viewer"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data

def test_login(client: TestClient, session: Session):
    # Prepare user
    hashed_password = get_password_hash("testpass")
    user = User(email="test@example.com", hashed_password=hashed_password, role="admin", is_active=True)
    session.add(user)
    session.commit()

    # Test login
    response = client.post(
        "/api/v1/auth/login/access-token",
        data={"username": "test@example.com", "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_read_user_me(client: TestClient, session: Session):
    # Prepare user
    hashed_password = get_password_hash("testpass")
    user = User(email="me@example.com", hashed_password=hashed_password, role="viewer", is_active=True)
    session.add(user)
    session.commit()

    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login/access-token",
        data={"username": "me@example.com", "password": "testpass"}
    )
    token = login_response.json()["access_token"]

    # Access protected route
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"

def test_invalid_login(client: TestClient):
    response = client.post(
        "/api/v1/auth/login/access-token",
        data={"username": "wrong@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"
