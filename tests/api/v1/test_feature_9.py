"""
Feature 9: Notifications & Alerts — Comprehensive API Tests

Tests notification creation via triggers, listing, mark-as-read,
and mark-all-as-read flows.
"""
import pytest
import uuid
from datetime import date
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.core.config import settings
from src.core.security import create_access_token
from src.models.notification import Notification
from src.models.user import User
from src.models.masjid import Masjid
from src.models.account import Account
from src.models.masjid_member import MasjidMember


# ── helpers ──────────────────────────────────────────────────
def _make_admin_headers(user_id, masjid_id) -> dict:
    token = create_access_token(subject=str(user_id), role="admin", masjid_id=str(masjid_id))
    return {"Authorization": f"Bearer {token}"}


def _seed_base(session: Session, suffix: str = ""):
    """Create a user, masjid, masjid_member (admin), and account."""
    uid = uuid.uuid4().hex[:8]
    user = User(email=f"f9_{uid}{suffix}@test.com", hashed_password="hashed", is_active=True)
    session.add(user)
    masjid = Masjid(
        name=f"F9 Masjid {uid}", slug=f"f9-masjid-{uid}",
        address="Test", city="Test", country="BD", contact_email=f"m{uid}@test.com",
    )
    session.add(masjid)
    session.commit()
    session.refresh(user)
    session.refresh(masjid)

    session.add(MasjidMember(user_id=user.id, masjid_id=masjid.id, role="admin"))
    account = Account(
        masjid_id=masjid.id, account_name="Cash Box", account_type="Cash",
        opening_balance=10000, opening_date=date(2026, 1, 1),
        created_by=user.id,
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    return user, masjid, account


# ── 1. Income creation triggers notification ────────────────
def test_income_creates_notification(client: TestClient, session: Session):
    user, masjid, account = _seed_base(session, "inc")
    headers = _make_admin_headers(user.id, masjid.id)

    response = client.post(
        f"{settings.API_V1_STR}/income/",
        headers=headers,
        json={
            "title": "Friday Collection F9",
            "amount": 5000,
            "currency": "BDT",
            "income_date": "2026-05-01",
            "category": "Friday Jumu'ah Collection",
            "payment_method": "Cash",
            "masjid_id": str(masjid.id),
            "account_id": str(account.id),
        },
    )
    assert response.status_code == 201

    notifs = session.exec(
        select(Notification).where(
            Notification.type == "income_recorded",
            Notification.user_id == user.id,
        )
    ).all()
    assert len(notifs) >= 1


# ── 2. Expense creation triggers notification ───────────────
def test_expense_creates_notification(client: TestClient, session: Session):
    user, masjid, account = _seed_base(session, "exp")
    headers = _make_admin_headers(user.id, masjid.id)

    response = client.post(
        f"{settings.API_V1_STR}/expense/",
        headers=headers,
        json={
            "title": "Electricity Bill F9",
            "amount": 3500,
            "currency": "BDT",
            "expense_date": "2026-05-01",
            "category": "Utility Bills",
            "payment_method": "Cash",
            "masjid_id": str(masjid.id),
            "account_id": str(account.id),
        },
    )
    assert response.status_code == 201

    notifs = session.exec(
        select(Notification).where(
            Notification.type == "expense_recorded",
            Notification.user_id == user.id,
        )
    ).all()
    assert len(notifs) >= 1


# ── 3. List notifications ───────────────────────────────────
def test_list_notifications(client: TestClient, session: Session):
    user, masjid, _ = _seed_base(session, "list")
    session.add(Notification(
        masjid_id=masjid.id, user_id=user.id,
        type="test", title="Test Alert", body="Test body", is_read=False,
    ))
    session.commit()

    headers = _make_admin_headers(user.id, masjid.id)
    response = client.get(f"{settings.API_V1_STR}/notifications/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


# ── 4. Mark single notification as read ──────────────────────
def test_mark_notification_read(client: TestClient, session: Session):
    user, masjid, _ = _seed_base(session, "read")
    n = Notification(
        masjid_id=masjid.id, user_id=user.id,
        type="test", title="Unread", body="Body", is_read=False,
    )
    session.add(n)
    session.commit()
    session.refresh(n)

    headers = _make_admin_headers(user.id, masjid.id)
    response = client.put(f"{settings.API_V1_STR}/notifications/{n.id}/read", headers=headers)
    assert response.status_code == 200
    assert response.json()["is_read"] is True


# ── 5. Mark all notifications as read ────────────────────────
def test_mark_all_notifications_read(client: TestClient, session: Session):
    user, masjid, _ = _seed_base(session, "all")
    for i in range(3):
        session.add(Notification(
            masjid_id=masjid.id, user_id=user.id,
            type="test", title=f"N{i}", body=f"Body{i}", is_read=False,
        ))
    session.commit()

    headers = _make_admin_headers(user.id, masjid.id)
    response = client.put(f"{settings.API_V1_STR}/notifications/read-all", headers=headers)
    assert response.status_code == 200
    assert "Marked" in response.json()["message"]


# ── 6. Filter unread notifications ───────────────────────────
def test_filter_unread_notifications(client: TestClient, session: Session):
    user, masjid, _ = _seed_base(session, "filter")
    session.add(Notification(
        masjid_id=masjid.id, user_id=user.id,
        type="test", title="Read One", body="Body", is_read=True,
    ))
    session.add(Notification(
        masjid_id=masjid.id, user_id=user.id,
        type="test", title="Unread One", body="Body", is_read=False,
    ))
    session.commit()

    headers = _make_admin_headers(user.id, masjid.id)
    response = client.get(
        f"{settings.API_V1_STR}/notifications/",
        params={"is_read": False},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert all(n["is_read"] is False for n in data)
